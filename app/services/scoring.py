from __future__ import annotations
from typing import Dict, List, Tuple
from math import isfinite

from app.models.schemas import PedidoScore, ScoreResposta, MotivosResposta
from app.services.dataset import find_empresa

# Tabelas simples (pode ajustar depois)
RATING_BASE = {
    "A+": 880, "A": 850, "A-": 820,
    "B+": 780, "B": 750, "B-": 720,
    "C+": 680, "C": 650, "C-": 620,
    "D": 580
}

SETOR_BONUS = {
    "Tecnologia": 20, "Saúde": 10, "Serviços": 0, "Comércio": 0,
    "Indústria": 0, "Agronegócio": 0,
    "Alimentação": -5, "Educação": -5, "Transportes": -10, "Turismo": -15,
}

POS_KEYWORDS = ("investimento", "expansão", "oportunidad", "novo produto")
NEG_KEYWORDS = ("inconsist", "insatisfa", "mudanças clim", "cuidado", "aumento no custo", "legislação")

def _coalesce_payload(p: PedidoScore):
    """Completa os dados a partir do dataset quando vier só 'empresa'."""
    motivos: List[str] = []
    data = {
        "empresa": p.empresa,
        "receita_anual": p.receita_anual,
        "divida_total": p.divida_total,
        "prazo_pagamento_dias": p.prazo_pagamento_dias,
        "setor": p.setor,
        "rating": p.rating,
        "noticias_recentes": p.noticias_recentes,
    }

    if p.empresa and any(v is None for k, v in data.items() if k != "empresa"):
        row = find_empresa(p.empresa)
        if not row:
            raise ValueError(f"Empresa '{p.empresa}' não encontrada no dataset.")
        for k, v in row.items():
            if data.get(k) is None and v is not None:
                data[k] = v
        motivos.append("Dados preenchidos a partir do dataset do desafio.")

    # valida mínimo necessário
    req = ["empresa", "receita_anual", "divida_total", "prazo_pagamento_dias", "setor", "rating"]
    faltando = [k for k in req if data.get(k) in (None, "")]
    if faltando:
        raise ValueError(f"Campos faltantes: {', '.join(faltando)}")

    return data, motivos

def _ajuste_setor(setor: str) -> int:
    return SETOR_BONUS.get(setor, 0)

def _ajuste_noticias(noticias: str) -> int:
    if not noticias:
        return 0
    txt = noticias.lower()
    pos = any(k in txt for k in POS_KEYWORDS)
    neg = any(k in txt for k in NEG_KEYWORDS)
    if pos and not neg:
        return 15
    if neg and not pos:
        return -15
    return 0

def _ajuste_prazo(dias: int) -> int:
    if dias is None:
        return 0
    if dias < 30:
        return 10
    if 30 <= dias <= 60:
        return 0
    if 61 <= dias <= 90:
        return -10
    return -20

def _faixa(score: int) -> str:
    if score >= 820:
        return "baixíssimo"
    if score >= 760:
        return "baixo"
    if score >= 700:
        return "médio"
    if score >= 640:
        return "alto"
    return "altíssimo"

def _clip(n: float, a: int, b: int) -> int:
    return int(max(a, min(b, round(n))))

def _calc_limite(receita_anual: float, rating: str, ratio: float) -> int:
    base_frac = {
        "A+": 0.45, "A": 0.40, "A-": 0.35,
        "B+": 0.30, "B": 0.27, "B-": 0.24,
        "C+": 0.20, "C": 0.17, "C-": 0.14,
        "D": 0.10
    }.get(rating, 0.18)

    penal = 0.5 * min(max(ratio, 0), 1.0)  # até -50% quando ratio >= 1
    frac = max(base_frac * (1.0 - penal), 0.05)
    return int(round(receita_anual * frac))

def calcular_score(pedido: PedidoScore) -> ScoreResposta:
    data, _ = _coalesce_payload(pedido)

    rating = str(data["rating"]).strip().upper()
    base = RATING_BASE.get(rating, 700)

    receita = float(data["receita_anual"])
    divida = float(data["divida_total"])
    ratio = (divida / receita) if (isfinite(divida) and isfinite(receita) and receita > 0) else 1.5

    score = base
    score += _ajuste_setor(str(data["setor"]))
    score += _ajuste_noticias(str(data.get("noticias_recentes") or ""))
    score += _ajuste_prazo(int(data["prazo_pagamento_dias"]))
    score -= min(ratio, 3.0) * 120  # penaliza endividamento

    score = _clip(score, 300, 900)
    faixa = _faixa(score)
    limite = _calc_limite(receita, rating, ratio)

    return ScoreResposta(
        empresa=str(data["empresa"]),
        score=score,
        limite_sugerido=limite,
        faixa_risco=faixa
    )

def explicar_motivos(pedido: PedidoScore) -> MotivosResposta:
    data, motivos = _coalesce_payload(pedido)

    receita = float(data["receita_anual"])
    divida = float(data["divida_total"])
    ratio = (divida / receita) if receita > 0 else float("inf")
    rating = str(data["rating"]).strip().upper()
    setor = str(data["setor"])
    noticias = str(data.get("noticias_recentes") or "")
    prazo = int(data["prazo_pagamento_dias"])

    if ratio <= 0.5:
        motivos.append("Endividamento/Receita saudável (até 50%).")
    elif ratio <= 1.0:
        motivos.append("Endividamento moderado (até 100% da receita).")
    else:
        motivos.append("Endividamento elevado (acima de 100% da receita).")

    if rating in ("A+", "A", "A-"):
        motivos.append(f"Rating {rating} favorece aprovação.")
    elif rating in ("B+", "B", "B-"):
        motivos.append(f"Rating {rating} intermediário.")
    else:
        motivos.append(f"Rating {rating} desfavorável.")

    sb = _ajuste_setor(setor)
    if sb > 0:
        motivos.append(f"Setor '{setor}' tradicionalmente resiliente no modelo.")
    elif sb < 0:
        motivos.append(f"Setor '{setor}' com maior volatilidade no modelo.")

    nb = _ajuste_noticias(noticias)
    if nb > 0:
        motivos.append("Notícia recente positiva.")
    elif nb < 0:
        motivos.append("Notícia recente negativa.")

    pb = _ajuste_prazo(prazo)
    if pb > 5:
        motivos.append("Prazo de pagamento curto contribui positivamente.")
    elif pb < -5:
        motivos.append("Prazo de pagamento longo aumenta risco de caixa.")

    return MotivosResposta(
        empresa=str(data["empresa"]),
        motivos=motivos
    )

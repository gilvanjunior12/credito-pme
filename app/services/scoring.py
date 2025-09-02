from typing import List, Tuple
from app.models.schemas import PedidoScore, ScoreResposta, MotivoItem

def _calcular_componentes(p: PedidoScore) -> tuple[int, int, int, int, int, int]:
    base = 300
    fat_pts = min(int(p.faturamento_mensal / 100), 150)
    tempo_pts = min(p.tempo_atividade_meses, 150)
    inad_pts = 50 if not p.inadimplente else -120
    emp_pts = min(max(p.empregados - 1, 0) * 5, 40)
    bonus_setor = {"Comercio": 10, "Servicos": 0, "Industria": 15, "Tecnologia": 25, "Agro": 10, "Outros": 0}
    setor_pts = bonus_setor.get(p.setor, 0)
    return base, fat_pts, tempo_pts, inad_pts, emp_pts, setor_pts

def calcular_basico(p: PedidoScore) -> ScoreResposta:
    base, fat_pts, tempo_pts, inad_pts, emp_pts, setor_pts = _calcular_componentes(p)
    score = base + fat_pts + tempo_pts + inad_pts + emp_pts + setor_pts
    score = max(0, min(score, 1000))
    aprovado = score >= 600
    limite_sugerido = int((score / 1000) * p.faturamento_mensal)
    return ScoreResposta(score=score, aprovado=aprovado, limite_sugerido=limite_sugerido)

def calcular_com_motivos(p: PedidoScore) -> tuple[ScoreResposta, List[MotivoItem]]:
    base, fat_pts, tempo_pts, inad_pts, emp_pts, setor_pts = _calcular_componentes(p)
    resp = calcular_basico(p)
    motivos = [
        MotivoItem(fator="faturamento", pontos=fat_pts,
                   motivo=f"{'+' if fat_pts >= 0 else ''}{fat_pts} por faturamento mensal de ~R${int(p.faturamento_mensal)} (máx +150)"),
        MotivoItem(fator="tempo_atividade", pontos=tempo_pts,
                   motivo=f"{'+' if tempo_pts >= 0 else ''}{tempo_pts} por {p.tempo_atividade_meses} meses operando (máx +150)"),
        MotivoItem(fator="inadimplencia", pontos=inad_pts,
                   motivo="+50 sem inadimplência" if inad_pts > 0 else "-120 com inadimplência"),
        MotivoItem(fator="empregados", pontos=emp_pts,
                   motivo=f"{'+' if emp_pts >= 0 else ''}{emp_pts} por {p.empregados} empregados (5 por extra, máx +40)"),
        MotivoItem(fator="setor", pontos=setor_pts,
                   motivo=f"{'+' if setor_pts >= 0 else ''}{setor_pts} para setor '{p.setor}'"),
    ]
    return resp, motivos

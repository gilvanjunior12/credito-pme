# -----------------------------------------------------------------------------
# Carrega os dados fictícios do desafio (JSON/CSV/Parquet/XML),
# padroniza nomes de colunas e fornece lookup por empresa.
# Mantém um cache em memória (_DATAFRAME) para evitar reler disco a cada request.
# -----------------------------------------------------------------------------

from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd

# Pasta de dados (app/data)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# Cache global do DataFrame
_DATAFRAME: Optional[pd.DataFrame] = None

# Mapeamento de nomes originais -> nomes padronizados
COLMAP = {
    "Empresa": "empresa",
    "Receita Anual": "receita_anual",
    "Receita_Anual": "receita_anual",
    "Dívida Total": "divida_total",
    "Divida Total": "divida_total",
    "Dívida_Total": "divida_total",
    "Prazo de Pagamento (dias)": "prazo_pagamento_dias",
    "Prazo_de_Pagamento_dias": "prazo_pagamento_dias",
    "Setor": "setor",
    "Rating": "rating",
    "Notícias Recentes": "noticias_recentes",
    "Noticias Recentes": "noticias_recentes",
    "Notícias_Recentes": "noticias_recentes",
}

# Ordem/corte final das colunas usadas pelo serviço
PADRONIZADAS = [
    "empresa", "receita_anual", "divida_total", "prazo_pagamento_dias",
    "setor", "rating", "noticias_recentes"
]

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renomeia e tipa colunas, e remove linhas inválidas."""
    # renomeia para o padrão interno
    rename_map = {col: COLMAP[col] for col in df.columns if col in COLMAP}
    df = df.rename(columns=rename_map)

    # mantém apenas as colunas padronizadas (na ordem)
    cols = [c for c in PADRONIZADAS if c in df.columns]
    df = df[cols].copy()

    # tipagem básica
    if "receita_anual" in df.columns:
        df["receita_anual"] = pd.to_numeric(df["receita_anual"], errors="coerce")
    if "divida_total" in df.columns:
        df["divida_total"] = pd.to_numeric(df["divida_total"], errors="coerce")
    if "prazo_pagamento_dias" in df.columns:
        df["prazo_pagamento_dias"] = pd.to_numeric(df["prazo_pagamento_dias"], errors="coerce")

    # limpeza de strings
    for col in ["empresa", "setor", "rating", "noticias_recentes"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # remove empresas vazias
    if "empresa" in df.columns:
        df = df[df["empresa"].notna() & (df["empresa"].str.len() > 0)]

    return df.reset_index(drop=True)

def _read_any() -> pd.DataFrame:
    """Lê o primeiro arquivo disponível (JSON/CSV/Parquet/XML) e normaliza."""
    jsonp = DATA_DIR / "dadoscreditoficticios.json"
    csvp = DATA_DIR / "dadoscreditoficticios.csv"
    parq = DATA_DIR / "dadoscreditoficticios.parquet"
    xmlp = DATA_DIR / "dadoscreditoficticios.xml"

    if jsonp.exists():
        # Tenta JSON "linhas" (NDJSON). Se não for, cai para JSON normal.
        try:
            df = pd.read_json(jsonp, lines=True)
        except ValueError:
            df = pd.read_json(jsonp)
    elif csvp.exists():
        df = pd.read_csv(csvp)
    elif parq.exists():
        df = pd.read_parquet(parq)
    elif xmlp.exists():
        df = pd.read_xml(xmlp)
    else:
        raise FileNotFoundError(
            "Nenhum dataset encontrado em app/data (esperado: .json/.csv/.parquet/.xml)."
        )

    return _normalize_columns(df)

def load_dataset() -> pd.DataFrame:
    """Retorna o DataFrame do cache; se vazio, carrega do disco uma vez."""
    global _DATAFRAME
    if _DATAFRAME is None:
        _DATAFRAME = _read_any()
    return _DATAFRAME

def find_empresa(nome: str) -> Optional[Dict[str, Any]]:
    """Busca case-insensitive por nome exato; se não achar, tenta prefixo."""
    if not nome:
        return None
    df = load_dataset()
    sel = df[df["empresa"].str.lower() == nome.strip().lower()]
    if sel.empty:
        sel = df[df["empresa"].str.lower().str.startswith(nome.strip().lower())]
    if sel.empty:
        return None
    return sel.iloc[0].to_dict()

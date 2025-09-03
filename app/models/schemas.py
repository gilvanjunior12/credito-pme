# -----------------------------------------------------------------------------
# Modelos Pydantic de entrada/saída da API.
# - PedidoScore: payload recebido nos endpoints (empresa ou campos completos).
# - ScoreResposta: retorno com score, limite e faixa de risco.
# - MotivosResposta: retorno com lista de motivos.
# Observação: manter campos opcionais permite completar via dataset pelo serviço.
# -----------------------------------------------------------------------------

from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field

class PedidoScore(BaseModel):
    """Entrada dos endpoints de scoring.
    Pode vir só com 'empresa' (o serviço completa com o dataset),
    ou com todos os campos preenchidos manualmente.
    """
    empresa: Optional[str] = Field(default=None, description="Nome da empresa no dataset")
    receita_anual: Optional[float] = Field(default=None, description="Receita anual da empresa")
    divida_total: Optional[float] = Field(default=None, description="Dívida total da empresa")
    prazo_pagamento_dias: Optional[int] = Field(default=None, description="Prazo médio de pagamento (dias)")
    setor: Optional[str] = Field(default=None, description="Setor de atuação")
    rating: Optional[str] = Field(default=None, description="Rating de crédito (A+, A, B, ...)")
    noticias_recentes: Optional[str] = Field(default=None, description="Resumo curto de notícias recentes")

class ScoreResposta(BaseModel):
    """Saída do /v1/score: resultado consolidado do cálculo."""
    empresa: str
    score: int
    limite_sugerido: int
    faixa_risco: str

class MotivosResposta(BaseModel):
    """Saída do /v1/score/motivos: explicações do resultado."""
    empresa: str
    motivos: List[str]

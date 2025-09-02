from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field

class PedidoScore(BaseModel):
    # Você pode mandar só 'empresa' (e a API completa pelos dados do dataset),
    # ou mandar os campos abaixo diretamente.
    empresa: Optional[str] = Field(default=None, example="Empresa 29")
    receita_anual: Optional[float] = Field(default=None, example=672834)
    divida_total: Optional[float] = Field(default=None, example=119351)
    prazo_pagamento_dias: Optional[int] = Field(default=None, example=56)
    setor: Optional[str] = Field(default=None, example="Tecnologia")
    rating: Optional[str] = Field(default=None, example="A+")
    noticias_recentes: Optional[str] = Field(
        default=None,
        example="Investimento em tecnologia de prevenção de fraudes."
    )

class ScoreResposta(BaseModel):
    empresa: str
    score: int
    limite_sugerido: int
    faixa_risco: str

class MotivosResposta(BaseModel):
    empresa: str
    motivos: List[str]

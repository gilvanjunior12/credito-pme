from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal, List

class PedidoScore(BaseModel):
    cnpj: str = Field(..., description="CNPJ da empresa (com ou sem máscara)")
    faturamento_mensal: Optional[float] = Field(None, gt=0, description="Receita média mensal em R$")
    faturamento_anual: Optional[float] = Field(None, gt=0, description="Receita anual em R$ (será dividido por 12)")
    tempo_atividade_meses: Optional[int] = Field(None, ge=0, description="Meses de operação")
    meses_operando: Optional[int] = Field(None, ge=0, description="Meses de operação (nome alternativo)")
    inadimplente: bool
    setor: Literal["Comercio", "Servicos", "Industria", "Tecnologia", "Agro", "Outros"] = "Outros"
    empregados: int = Field(0, ge=0)

    @field_validator("cnpj")
    @classmethod
    def _limpa_cnpj(cls, v: str) -> str:
        return "".join(ch for ch in v if ch.isdigit())

    @model_validator(mode="after")
    def _resolver_campos_alternativos(self):
        if self.faturamento_mensal is None and self.faturamento_anual is not None:
            self.faturamento_mensal = self.faturamento_anual / 12.0
        if self.tempo_atividade_meses is None and self.meses_operando is not None:
            self.tempo_atividade_meses = self.meses_operando
        if self.faturamento_mensal is None:
            raise ValueError("Informe 'faturamento_mensal' OU 'faturamento_anual'.")
        if self.tempo_atividade_meses is None:
            raise ValueError("Informe 'tempo_atividade_meses' OU 'meses_operando'.")
        return self


class ScoreResposta(BaseModel):
    score: int
    aprovado: bool
    limite_sugerido: int


class MotivoItem(BaseModel):
    fator: str
    pontos: int
    motivo: str


class MotivosResposta(BaseModel):
    score: int
    aprovado: bool
    limite_sugerido: int
    breakdown: List[MotivoItem]

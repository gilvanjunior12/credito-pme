from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional

app = FastAPI(title="Crédito PME API", version="0.2.0")


class ScoreResposta(BaseModel):
    score: int
    aprovado: bool
    limite_sugerido: int


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


def calcular_score(p: PedidoScore) -> dict:
    score = 300
    score += min(int(p.faturamento_mensal / 100), 150)
    score += min(p.tempo_atividade_meses, 150)
    score += 50 if not p.inadimplente else -120
    score += min(max(p.empregados - 1, 0) * 5, 40)
    bonus_setor = {"Comercio": 10, "Servicos": 0, "Industria": 15, "Tecnologia": 25, "Agro": 10, "Outros": 0}
    score += bonus_setor.get(p.setor, 0)
    score = max(0, min(score, 1000))
    aprovado = score >= 600
    limite_sugerido = int((score / 1000) * p.faturamento_mensal * 1.0)
    return {"score": score, "aprovado": aprovado, "limite_sugerido": limite_sugerido}


@app.get("/")
def root():
    return {"mensagem": "API de Crédito PME rodando!"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/v1/score", response_model=ScoreResposta)
def score(pedido: PedidoScore):
    return calcular_score(pedido)

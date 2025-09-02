import os
from typing import Literal, Optional, List, Tuple

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, model_validator
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Crédito PME API (DEV)"),
    version="0.3.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


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


def _calcular_e_motivos(p: PedidoScore) -> Tuple[ScoreResposta, List[MotivoItem]]:
    base = 300
    fat_pts = min(int(p.faturamento_mensal / 100), 150)
    tempo_pts = min(p.tempo_atividade_meses, 150)
    inad_pts = 50 if not p.inadimplente else -120
    emp_pts = min(max(p.empregados - 1, 0) * 5, 40)
    bonus_setor = {"Comercio": 10, "Servicos": 0, "Industria": 15, "Tecnologia": 25, "Agro": 10, "Outros": 0}
    setor_pts = bonus_setor.get(p.setor, 0)
    score = base + fat_pts + tempo_pts + inad_pts + emp_pts + setor_pts
    score = max(0, min(score, 1000))
    aprovado = score >= 600
    limite_sugerido = int((score / 1000) * p.faturamento_mensal)
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
                   motivo=f"{'+' if setor_pts >= 0 else ''}{setor_pts} para setor '{p.setor}'")
    ]
    return ScoreResposta(score=score, aprovado=aprovado, limite_sugerido=limite_sugerido), motivos


@app.get("/", include_in_schema=False)
def root():
    return {"mensagem": "API de Crédito PME rodando!"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.post("/v1/score", response_model=ScoreResposta)
def score(pedido: PedidoScore):
    resposta, _ = _calcular_e_motivos(pedido)
    return resposta


@app.post("/v1/score/motivos", response_model=MotivosResposta)
def score_motivos(pedido: PedidoScore):
    resposta, motivos = _calcular_e_motivos(pedido)
    return {
        "score": resposta.score,
        "aprovado": resposta.aprovado,
        "limite_sugerido": resposta.limite_sugerido,
        "breakdown": motivos
    }

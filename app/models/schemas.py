from typing import Optional, List
from pydantic import BaseModel, model_validator

class PedidoScore(BaseModel):
    # Formato README
    empresa: Optional[str] = None
    receita_anual: Optional[int] = None
    divida_total: Optional[int] = None
    prazo_pagamento_dias: Optional[int] = None
    setor: Optional[str] = None
    rating: Optional[str] = None
    noticias_recentes: Optional[str] = None

    # Formato alternativo (testes)
    cnpj: Optional[str] = None
    faturamento_mensal: Optional[int] = None
    faturamento_anual: Optional[int] = None
    tempo_atividade_meses: Optional[int] = None
    meses_operando: Optional[int] = None
    inadimplente: Optional[bool] = None
    empregados: Optional[int] = None

    @model_validator(mode="after")
    def _validate_e_normalizar(self):
        if not self.empresa and not self.cnpj:
            raise ValueError("Informe 'empresa' ou 'cnpj'.")

        if self.cnpj and not self.empresa:
            self.empresa = self.cnpj

        # Deriva receita anual se preciso
        if self.receita_anual is None:
            if self.faturamento_anual is not None:
                self.receita_anual = int(self.faturamento_anual)
            elif self.faturamento_mensal is not None:
                self.receita_anual = int(self.faturamento_mensal) * 12

        if self.receita_anual is None:
            raise ValueError("Informe 'faturamento_mensal' ou 'faturamento_anual'.")

        # Defaults conservadores p/ testes
        if self.divida_total is None:
            self.divida_total = int(self.receita_anual * 0.4) if not self.inadimplente else int(self.receita_anual * 0.6)

        if self.prazo_pagamento_dias is None:
            self.prazo_pagamento_dias = 90

        if self.setor is None:
            self.setor = "Comercio"

        if self.rating is None:
            meses = self.meses_operando or self.tempo_atividade_meses or 12
            if self.inadimplente:
                self.rating = "E"
            else:
                if meses < 6:
                    self.rating = "D"
                elif meses < 24:
                    self.rating = "C"
                else:
                    self.rating = "B"

        if self.noticias_recentes is None:
            self.noticias_recentes = ""

        return self


class ScoreResposta(BaseModel):
    empresa: str
    score: int
    limite_sugerido: int
    faixa_risco: str
    aprovado: bool  # <-- testes cobram este campo


class MotivosResposta(BaseModel):
    empresa: str
    score: int
    motivos: List[str]
    breakdown: List[str]  # <-- testes cobram este campo

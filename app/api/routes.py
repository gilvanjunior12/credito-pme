from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.schemas import PedidoScore, ScoreResposta, MotivosResposta
from app.services.scoring import calcular_score, explicar_motivos

router = APIRouter()

@router.post("/v1/score", response_model=ScoreResposta)
def post_score(pedido: PedidoScore) -> ScoreResposta:
    try:
        return calcular_score(pedido)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/v1/score/motivos", response_model=MotivosResposta)
def post_motivos(pedido: PedidoScore) -> MotivosResposta:
    try:
        return explicar_motivos(pedido)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

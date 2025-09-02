from fastapi import APIRouter
from app.models.schemas import PedidoScore, ScoreResposta, MotivosResposta
from app.services.scoring import calcular_basico, calcular_com_motivos

router = APIRouter(prefix="/v1")

@router.post("/score", response_model=ScoreResposta)
def score(pedido: PedidoScore):
    return calcular_basico(pedido)

@router.post("/score/motivos", response_model=MotivosResposta)
def score_motivos(pedido: PedidoScore):
    resp, motivos = calcular_com_motivos(pedido)
    return {
        "score": resp.score,
        "aprovado": resp.aprovado,
        "limite_sugerido": resp.limite_sugerido,
        "breakdown": motivos,
    }

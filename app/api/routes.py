# -----------------------------------------------------------------------------
# Endpoints públicos da API (FastAPI). Mapeia pedidos para o serviço de scoring.
# Converte erros de negócio em HTTP claro para o cliente (ex.: 404 empresa).
# -----------------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import PedidoScore, ScoreResposta, MotivosResposta
from app.services.scoring import calcular_score, explicar_motivos

router = APIRouter()

@router.post("/v1/score", response_model=ScoreResposta)
async def post_score(pedido: PedidoScore, request: Request):
    """
    Calcula score/limite/faixa. Aceita só 'empresa' ou o payload completo.
    """
    try:
        return calcular_score(pedido)
    except ValueError as e:
        msg = str(e)
        # Se a mensagem indicar que a empresa não foi encontrada, devolve 404
        if "não encontrada" in msg:
            raise HTTPException(status_code=404, detail=msg)
        # Para outras validações (campos faltantes etc.), usa 422
        raise HTTPException(status_code=422, detail=msg)

@router.post("/v1/score/motivos", response_model=MotivosResposta)
async def post_motivos(pedido: PedidoScore, request: Request):
    """
    Retorna apenas a lista de 'motivos' explicando o resultado do modelo.
    """
    try:
        return explicar_motivos(pedido)
    except ValueError as e:
        msg = str(e)
        if "não encontrada" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=422, detail=msg)

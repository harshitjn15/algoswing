from fastapi import APIRouter
from app.services.overlay_service import OverlayService, ChartOverlaysResponse

router = APIRouter(prefix="/chart-overlays", tags=["Chart Overlays"])

@router.get("/{symbol}", response_model=ChartOverlaysResponse)
async def get_chart_overlays(symbol: str):
    """
    Returns generic annotations to draw on the chart.
    The logic is delegated to the OverlayService to decouple API from business logic.
    """
    service = OverlayService()
    return await service.get_overlays(symbol)


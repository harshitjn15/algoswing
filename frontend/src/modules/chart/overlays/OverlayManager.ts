import { IChartWidgetApi } from "../types/tradingview";
import { OverlayData } from "../services/chart.service";

export class OverlayManager {
  private chartApi: IChartWidgetApi | null = null;
  private drawnEntities: string[] = [];

  setChartApi(api: IChartWidgetApi) {
    this.chartApi = api;
  }

  /**
   * Clears existing overlays and renders the newly provided ones.
   */
  render(overlays: OverlayData[]) {
    this.clear();
    
    if (!this.chartApi) return;

    overlays.forEach(overlay => {
      try {
        const entityId = this.chartApi!.createShape(
          { price: overlay.price },
          { 
            shape: "horizontal_line", 
            text: overlay.label,
            overrides: {
              linecolor: overlay.color || "#2962FF",
              textcolor: overlay.color || "#2962FF",
              linewidth: 2,
            }
          }
        );
        if (entityId) {
          this.drawnEntities.push(entityId);
        }
      } catch (e) {
        console.warn(`Failed to render overlay ${overlay.label}:`, e);
      }
    });
  }

  clear() {
    if (!this.chartApi) return;
    
    this.drawnEntities.forEach(entityId => {
      try {
        this.chartApi!.removeEntity(entityId);
      } catch (e) {
        // Ignore errors if entity already removed
      }
    });
    this.drawnEntities = [];
  }
}


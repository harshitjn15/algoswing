import { Bar, LibrarySymbolInfo, SearchSymbolResultItem } from "../types/tradingview";

const API_BASE = "http://localhost:8000/api/v1";

export interface OverlayData {
  type: string;
  price: number;
  label: string;
  color?: string;
}

export interface ChartOverlaysResponse {
  ath?: OverlayData;
  breakout?: OverlayData;
  retest?: OverlayData;
  entry?: OverlayData;
  sl?: OverlayData;
  targets: OverlayData[];
}

export class ChartService {
  static async getBars(
    symbol: string,
    resolution: string,
    from: number,
    to: number
  ): Promise<Bar[]> {
    const url = new URL(`${API_BASE}/market-data/candles`);
    url.searchParams.append("symbol", symbol);
    url.searchParams.append("resolution", resolution);
    url.searchParams.append("from", from.toString());
    url.searchParams.append("to", to.toString());

    const response = await fetch(url.toString());
    if (!response.ok) {
      throw new Error(`Failed to fetch candles: ${response.statusText}`);
    }
    return response.json();
  }

  static async resolveSymbol(symbolName: string): Promise<any> {
    const response = await fetch(`${API_BASE}/symbols/${encodeURIComponent(symbolName)}`);
    if (!response.ok) {
      throw new Error(`Failed to resolve symbol: ${response.statusText}`);
    }
    return response.json();
  }

  static async searchSymbols(query: string): Promise<any[]> {
    const url = new URL(`${API_BASE}/symbols/search`);
    url.searchParams.append("query", query);

    const response = await fetch(url.toString());
    if (!response.ok) {
      throw new Error(`Failed to search symbols: ${response.statusText}`);
    }
    return response.json();
  }

  static async fetchOverlays(symbol: string): Promise<ChartOverlaysResponse | null> {
    const response = await fetch(`${API_BASE}/chart-overlays/${encodeURIComponent(symbol)}`);
    if (!response.ok) {
      if (response.status === 404) return null;
      throw new Error(`Failed to fetch overlays: ${response.statusText}`);
    }
    return response.json();
  }
}

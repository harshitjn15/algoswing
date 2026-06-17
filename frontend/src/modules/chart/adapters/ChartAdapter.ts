import { Bar, LibrarySymbolInfo, SearchSymbolResultItem } from "../types/tradingview";
import { ChartService } from "../services/chart.service";

/**
 * Adapter that connects TradingView's Datafeed API with our Application's ChartService.
 * This ensures our components and services don't depend on proprietary TV UDF formats.
 */
export class ChartAdapter {
  
  static async searchSymbols(userInput: string): Promise<SearchSymbolResultItem[]> {
    const rawSymbols = await ChartService.searchSymbols(userInput);
    // Map application symbols to TV format if needed
    return rawSymbols.map(s => ({
      symbol: s.symbol,
      full_name: s.full_name,
      description: s.description,
      exchange: s.exchange,
      ticker: s.symbol, // TV uses ticker for resolution
      type: s.type
    }));
  }

  static async resolveSymbol(symbolName: string): Promise<LibrarySymbolInfo> {
    const info = await ChartService.resolveSymbol(symbolName);
    return {
      name: info.name,
      full_name: info.name,
      ticker: info.ticker,
      description: info.description,
      type: info.type,
      session: info.timezone === "Asia/Kolkata" ? "0915-1530" : "24x7",
      exchange: info.exchange,
      listed_exchange: info.exchange,
      timezone: info.timezone,
      format: "price",
      pricescale: 100,
      minmov: 1,
      has_intraday: false,
      has_daily: true,
      has_weekly_and_monthly: true,
      supported_resolutions: ["1D", "1W", "1M"],
      volume_precision: 0,
      data_status: "streaming"
    };
  }

  static async getHistoricalBars(symbolInfo: LibrarySymbolInfo, resolution: string, from: number, to: number): Promise<Bar[]> {
    const bars = await ChartService.getBars(symbolInfo.name, resolution, from, to);
    // TV expects array of Bar objects. Our service already returns {time, open, high, low, close, volume}
    return bars;
  }
}

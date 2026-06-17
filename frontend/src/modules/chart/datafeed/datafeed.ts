import { IDatafeedChartApi } from "../types/tradingview";
import { ChartAdapter } from "../adapters/ChartAdapter";

export const datafeed: IDatafeedChartApi = {
  onReady: (callback) => {
    console.log("[datafeed] onReady called");
    setTimeout(() => {
      callback({
        supported_resolutions: ["5", "15", "60", "240", "1D", "1W", "1M"],
        exchanges: [
          { value: "NSE", name: "NSE", desc: "National Stock Exchange" },
        ],
        symbols_types: [
          { name: "Stock", value: "stock" },
        ],
      });
    }, 0);
  },

  searchSymbols: async (userInput, exchange, symbolType, onResultReadyCallback) => {
    console.log("[datafeed] searchSymbols called");
    try {
      const symbols = await ChartAdapter.searchSymbols(userInput);
      onResultReadyCallback(symbols);
    } catch (error) {
      console.error("[datafeed] Search error:", error);
      onResultReadyCallback([]);
    }
  },

  resolveSymbol: async (symbolName, onSymbolResolvedCallback, onResolveErrorCallback) => {
    console.log("[datafeed] resolveSymbol:", symbolName);
    try {
      const symbolInfo = await ChartAdapter.resolveSymbol(symbolName);
      onSymbolResolvedCallback(symbolInfo);
    } catch (error) {
      console.error("[datafeed] Resolve error:", error);
      onResolveErrorCallback("unknown_symbol");
    }
  },

  getBars: async (symbolInfo, resolution, periodParams, onHistoryCallback, onErrorCallback) => {
    console.log("[datafeed] getBars:", symbolInfo.name, resolution, periodParams);
    try {
      const bars = await ChartAdapter.getHistoricalBars(symbolInfo, resolution, periodParams.from, periodParams.to);
      if (bars.length === 0) {
        onHistoryCallback([], { noData: true });
        return;
      }
      onHistoryCallback(bars, { noData: false });
    } catch (error) {
      console.error("[datafeed] getBars error:", error);
      onErrorCallback("Error fetching historical data");
    }
  },

  subscribeBars: (symbolInfo, resolution, onRealtimeCallback, subscriberUID, onResetCacheNeededCallback) => {
    console.log("[datafeed] subscribeBars:", subscriberUID);
    // Real-time streaming placeholder
    // In the future: WebSocket connections go here
  },

  unsubscribeBars: (subscriberUID) => {
    console.log("[datafeed] unsubscribeBars:", subscriberUID);
    // Real-time streaming placeholder
  },
};

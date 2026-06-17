/**
 * Minimal type declarations for TradingView Charting Library.
 * These act as placeholders to allow compilation without the proprietary .d.ts files.
 */

export interface LibrarySymbolInfo {
    name: string;
    full_name: string;
    ticker?: string;
    description: string;
    type: string;
    session: string;
    exchange: string;
    listed_exchange: string;
    timezone: string;
    format: "price";
    pricescale: number;
    minmov: number;
    has_intraday?: boolean;
    has_daily?: boolean;
    has_weekly_and_monthly?: boolean;
    supported_resolutions?: string[];
    volume_precision?: number;
    data_status?: "streaming" | "endofday" | "pulsed" | "delayed_streaming";
}

export interface Bar {
    time: number;
    open: number;
    high: number;
    low: number;
    close: number;
    volume?: number;
}

export interface SearchSymbolResultItem {
    symbol: string;
    full_name: string;
    description: string;
    exchange: string;
    ticker: string;
    type: string;
}

export interface IDatafeedChartApi {
    onReady(callback: (configuration: object) => void): void;
    searchSymbols(
        userInput: string,
        exchange: string,
        symbolType: string,
        onResultReadyCallback: (result: SearchSymbolResultItem[]) => void
    ): void;
    resolveSymbol(
        symbolName: string,
        onSymbolResolvedCallback: (symbolInfo: LibrarySymbolInfo) => void,
        onResolveErrorCallback: (reason: string) => void,
        extension?: any
    ): void;
    getBars(
        symbolInfo: LibrarySymbolInfo,
        resolution: string,
        periodParams: { from: number; to: number; firstDataRequest: boolean; countBack?: number },
        onHistoryCallback: (bars: Bar[], meta: { noData: boolean }) => void,
        onErrorCallback: (reason: string) => void
    ): void;
    subscribeBars(
        symbolInfo: LibrarySymbolInfo,
        resolution: string,
        onRealtimeCallback: (bar: Bar) => void,
        subscriberUID: string,
        onResetCacheNeededCallback: () => void
    ): void;
    unsubscribeBars(subscriberUID: string): void;
}

export interface ChartingLibraryWidgetOptions {
    symbol: string;
    interval: string;
    container: HTMLElement;
    datafeed: IDatafeedChartApi;
    library_path: string;
    locale: string;
    theme?: "Light" | "Dark";
    autosize?: boolean;
    fullscreen?: boolean;
    disabled_features?: string[];
    enabled_features?: string[];
    custom_css_url?: string;
    loading_screen?: { backgroundColor: string; foregroundColor: string };
    client_id?: string;
    user_id?: string;
}

export interface IChartingLibraryWidget {
    onChartReady(callback: () => void): void;
    remove(): void;
    chart(): IChartWidgetApi;
}

export interface IChartWidgetApi {
    createShape(point: any, options: any): string | null;
    createMultipointShape(points: any[], options: any): string | null;
    removeEntity(entityId: string): void;
}

declare global {
    interface Window {
        TradingView: {
            widget: {
                new (options: ChartingLibraryWidgetOptions): IChartingLibraryWidget;
            };
        };
    }
}

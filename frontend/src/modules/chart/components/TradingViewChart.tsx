"use client";

import React, { useEffect, useRef, useState } from "react";
import { useChartStore } from "../stores/chart.store";
import { datafeed } from "../datafeed/datafeed";
import { IChartingLibraryWidget } from "../types/tradingview";
import { OverlayManager } from "../overlays/OverlayManager";

import { ChartService } from "../services/chart.service";

export interface TradingViewChartProps {
  containerId?: string;
}

export const TradingViewChart: React.FC<TradingViewChartProps> = ({
  containerId = "tv_chart_container",
}) => {
  const { selectedSymbol, selectedInterval, selectedTheme } = useChartStore();
  const widgetRef = useRef<IChartingLibraryWidget | null>(null);
  const [isLibraryLoaded, setIsLibraryLoaded] = useState(false);
  const overlayManagerRef = useRef(new OverlayManager());

  useEffect(() => {
    const checkLibrary = setInterval(() => {
      if (typeof window !== "undefined" && window.TradingView && window.TradingView.widget) {
        setIsLibraryLoaded(true);
        clearInterval(checkLibrary);
      }
    }, 100);
    return () => clearInterval(checkLibrary);
  }, []);

  useEffect(() => {
    if (!isLibraryLoaded) return;

    if (widgetRef.current) {
      widgetRef.current.remove();
      widgetRef.current = null;
    }

    const widgetOptions = {
      symbol: selectedSymbol,
      interval: selectedInterval,
      container: document.getElementById(containerId) as HTMLElement,
      datafeed: datafeed,
      library_path: "/charting_library/",
      locale: "en",
      disabled_features: ["use_localstorage_for_settings"],
      enabled_features: ["study_templates"],
      theme: selectedTheme === "dark" ? "Dark" : "Light",
      autosize: true,
    } as any;

    try {
      const widget = new window.TradingView.widget(widgetOptions);
      widgetRef.current = widget;

      widget.onChartReady(() => {
        const chartApi = widget.chart();
        overlayManagerRef.current.setChartApi(chartApi);
        
        // Fetch and draw overlays for this symbol
        ChartService.fetchOverlays(selectedSymbol).then((data) => {
          if (data) {
            const overlays = [];
            if (data.ath) overlays.push(data.ath);
            if (data.breakout) overlays.push(data.breakout);
            if (data.retest) overlays.push(data.retest);
            if (data.entry) overlays.push(data.entry);
            if (data.sl) overlays.push(data.sl);
            if (data.targets) overlays.push(...data.targets);
            
            overlayManagerRef.current.render(overlays);
          }
        });
      });
    } catch (e) {
      console.error("Error initializing TradingView widget:", e);
    }

    return () => {
      if (widgetRef.current !== null) {
        widgetRef.current.remove();
        widgetRef.current = null;
      }
    };
  }, [isLibraryLoaded, selectedSymbol, selectedInterval, selectedTheme, containerId]);

  return (
    <div className="w-full h-full relative">
      {!isLibraryLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10 text-gray-400">
          <div className="flex flex-col items-center gap-2">
            <span className="loading loading-spinner loading-md"></span>
            <p>Loading Charting Library...</p>
            <p className="text-xs text-gray-500">Waiting for /charting_library/ to be mounted</p>
          </div>
        </div>
      )}
      <div id={containerId} className="w-full h-full" />
    </div>
  );
};

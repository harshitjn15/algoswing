"use client";

import React, { useEffect } from "react";
import { TradingViewChart } from "./TradingViewChart";
import { ChartToolbar } from "./ChartToolbar";
import { useChartStore } from "../stores/chart.store";

export const TradingTerminal: React.FC = () => {
  const { isFullscreen } = useChartStore();

  return (
    <div
      className={`flex flex-col bg-gray-900 border border-gray-800 shadow-xl overflow-hidden transition-all duration-300 ${
        isFullscreen
          ? "fixed inset-0 z-50 rounded-none h-screen w-screen"
          : "relative rounded-xl h-[600px] w-full"
      }`}
    >
      <ChartToolbar />
      <div className="flex-1 relative w-full h-full">
        <TradingViewChart containerId="main-chart" />
      </div>
    </div>
  );
};

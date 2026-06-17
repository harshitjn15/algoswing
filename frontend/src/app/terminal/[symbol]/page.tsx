"use client";

import React, { useEffect } from "react";
import { useParams } from "next/navigation";
import { TradingTerminal } from "@/modules/chart/components/TradingTerminal";
import { useChartStore } from "@/modules/chart/stores/chart.store";

export default function SymbolTerminalPage() {
  const params = useParams();
  const symbol = params.symbol as string;
  const setSymbol = useChartStore((state) => state.setSymbol);

  useEffect(() => {
    if (symbol) {
      // Decode URI component (e.g. NSE%3ARELIANCE -> NSE:RELIANCE)
      setSymbol(decodeURIComponent(symbol));
    }
  }, [symbol, setSymbol]);

  return (
    <div className="w-full h-screen bg-black">
      <TradingTerminal />
    </div>
  );
}

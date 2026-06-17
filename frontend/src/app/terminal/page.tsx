import React from "react";
import { TradingTerminal } from "@/modules/chart/components/TradingTerminal";

export const metadata = {
  title: "Trading Terminal | AlgoSwing",
  description: "Professional trading terminal with advanced charting",
};

export default function TerminalPage() {
  return (
    <div className="w-full h-screen bg-black">
      <TradingTerminal />
    </div>
  );
}

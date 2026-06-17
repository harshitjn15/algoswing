"use client";

import { Card, SectionHeader, EmptyState, Badge } from "@/components/ui";
import { BarChart2, Clock } from "lucide-react";

export default function BacktestingPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <SectionHeader
        title="Backtesting"
        subtitle="Historical strategy simulation — Phase 3"
        action={
          <Badge variant="warning" size="md">Coming in Phase 3</Badge>
        }
      />
      <EmptyState
        icon={<BarChart2 size={40} />}
        title="Backtesting Engine — Phase 3"
        description="Run IPO ATH Retest strategy against historical OHLCV data. Generates win rate, CAGR, Sharpe ratio, max drawdown, and equity curve."
      />
    </div>
  );
}

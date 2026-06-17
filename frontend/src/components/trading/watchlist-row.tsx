"use client";

import { WatchlistEntry } from "@/lib/api";
import { formatCurrency, formatPct, formatVolume, cn } from "@/lib/utils";
import { Card, Badge } from "@/components/ui";
import { TrendingUp, TrendingDown, BarChart3 } from "lucide-react";

interface WatchlistRowProps {
  entry: WatchlistEntry;
  marketOpen?: boolean;
}

export function WatchlistRow({ entry, marketOpen = false }: WatchlistRowProps) {
  const isNearAth = entry.near_ath;
  const distPct = entry.ath_distance_pct ?? 0;
  const volRatio = entry.volume_ratio ?? 0;

  return (
    <div className={cn(
      "flex items-center px-4 py-3 rounded-xl border transition-all duration-150",
      "hover:bg-slate-800/30 cursor-default",
      isNearAth
        ? "border-teal-500/20 bg-teal-500/5"
        : "border-slate-800/40 bg-slate-900/20"
    )}>
      {/* Symbol */}
      <div className="flex-[2] min-w-[100px]">
        <div className="flex items-center gap-2">
          <a 
            href={`https://in.tradingview.com/chart/?symbol=NSE:${entry.symbol}`} 
            target="_blank" 
            rel="noopener noreferrer"
            className="font-bold text-white font-mono text-sm hover:text-teal-400 hover:underline transition-colors"
          >
            {entry.symbol}
          </a>
          {isNearAth && (
            <span className="text-[10px] bg-teal-500/20 text-teal-400 px-1.5 py-0.5 rounded-full border border-teal-500/20 font-medium">
              NEAR ATH
            </span>
          )}
        </div>
        <p className="text-xs text-slate-500 mt-0.5">
          Listed {entry.listing_date ?? "—"}
        </p>
      </div>

      {/* Last Close */}
      <div className="flex-1 text-right hidden sm:block">
        <p className="text-sm font-semibold text-white font-mono flex items-center justify-end gap-1.5">
          {marketOpen && <span className="w-1.5 h-1.5 rounded-full bg-teal-500 animate-pulse" />}
          {entry.last_close ? formatCurrency(entry.last_close) : "—"}
        </p>
        <p className="text-xs text-slate-500">{marketOpen ? "Live Price" : "Last Close"}</p>
      </div>

      {/* ATH */}
      <div className="flex-1 text-right hidden md:block">
        <p className="text-sm font-mono text-slate-300">
          {entry.ath ? formatCurrency(entry.ath) : "—"}
        </p>
        <p className="text-xs text-slate-500">ATH</p>
      </div>

      {/* ATH Distance */}
      <div className="flex-1 text-right">
        <p className={cn(
          "text-sm font-bold font-mono flex items-center gap-1 justify-end",
          distPct >= 0 ? "text-emerald-400" : "text-red-400"
        )}>
          {distPct >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
          {formatPct(distPct, true)}
        </p>
        <p className="text-xs text-slate-500">ATH Dist</p>
      </div>

      {/* Volume Ratio */}
      <div className="flex-1 text-right hidden sm:block">
        <p className={cn(
          "text-sm font-bold font-mono flex items-center gap-1 justify-end",
          volRatio >= 1.5 ? "text-teal-400" : "text-slate-400"
        )}>
          <BarChart3 size={12} />
          {volRatio.toFixed(1)}x
        </p>
        <p className="text-xs text-slate-500">Vol Ratio</p>
      </div>

      {/* Strategy */}
      <div className="flex-1 flex justify-end hidden lg:flex">
        <Badge variant="muted" size="sm">
          {entry.scanner.replace(/_/g, " ")}
        </Badge>
      </div>
    </div>
  );
}

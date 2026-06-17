"use client";

import { Signal, api } from "@/lib/api";
import {
  formatCurrency,
  formatPct,
  formatVolume,
  timeAgo,
  getConfidenceBg,
  getStatusColor,
} from "@/lib/utils";
import { Badge, Card, Button } from "@/components/ui";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  TrendingUp,
  Shield,
  Target,
  BarChart3,
  Clock,
  Zap,
} from "lucide-react";

interface SignalCardProps {
  signal: Signal;
  compact?: boolean;
}

export function SignalCard({ signal, compact = false }: SignalCardProps) {
  const tp1 = signal.targets[0];
  const tp2 = signal.targets[1];
  const tp3 = signal.targets[2];

  const queryClient = useQueryClient();
  const { mutate, isPending } = useMutation({
    mutationFn: () =>
      api.paperTrades.create({
        signal_id: signal._id,
        user_id: "demo",
        symbol: signal.symbol,
        strategy_id: signal.strategy_id,
        entry_price: signal.entry,
        qty: 10, // default placeholder size
        stop_loss: signal.stop_loss,
        targets: signal.targets,
        risk_pct: signal.risk_pct,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["paperTrades"] });
    },
  });

  return (
    <Card
      hover
      className="animate-slide-in border border-slate-800/60 hover:border-teal-500/30"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <a 
              href={`https://in.tradingview.com/chart/?symbol=NSE:${signal.symbol}`} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-lg font-bold text-white font-mono hover:text-teal-400 hover:underline transition-colors"
            >
              {signal.symbol}
            </a>
            <Badge variant="muted" size="sm">{signal.exchange}</Badge>
          </div>
          <p className="text-xs text-slate-500">
            {signal.strategy_id?.replace(/_/g, " ").toUpperCase() || "UNKNOWN"} • {timeAgo(signal.generated_at)}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1.5">
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${getStatusColor(signal.status)}`}>
            {signal.status}
          </span>
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${getConfidenceBg(signal.confidence)}`}>
            {signal.confidence}
          </span>
        </div>
      </div>

      {/* Price Grid */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="bg-slate-800/40 rounded-lg p-2.5 text-center">
          <p className="text-[10px] text-slate-500 mb-1 flex items-center justify-center gap-1">
            <TrendingUp size={10} /> ENTRY
          </p>
          <p className="text-sm font-bold text-teal-400 font-mono">
            {formatCurrency(signal.entry)}
          </p>
        </div>
        <div className="bg-red-500/5 rounded-lg p-2.5 text-center border border-red-500/10">
          <p className="text-[10px] text-slate-500 mb-1 flex items-center justify-center gap-1">
            <Shield size={10} /> STOP LOSS
          </p>
          <p className="text-sm font-bold text-red-400 font-mono">
            {formatCurrency(signal.stop_loss)}
          </p>
        </div>
        <div className="bg-slate-800/40 rounded-lg p-2.5 text-center">
          <p className="text-[10px] text-slate-500 mb-1 flex items-center justify-center gap-1">
            <Zap size={10} /> RISK
          </p>
          <p className="text-sm font-bold text-amber-400 font-mono">
            {formatPct(signal.risk_pct)}
          </p>
        </div>
      </div>

      {/* Targets */}
      {!compact && (
        <div className="grid grid-cols-3 gap-2 mb-3">
          {[
            { label: "TP1", value: tp1, pct: 10 },
            { label: "TP2", value: tp2, pct: 15 },
            { label: "TP3", value: tp3, pct: 20 },
          ].map(({ label, value, pct }) => (
            <div key={label} className="bg-emerald-500/5 rounded-lg p-2.5 text-center border border-emerald-500/10">
              <p className="text-[10px] text-slate-500 mb-1 flex items-center justify-center gap-1">
                <Target size={10} /> {label}
              </p>
              <p className="text-xs font-bold text-emerald-400 font-mono">
                {value ? formatCurrency(value) : "—"}
              </p>
              <p className="text-[10px] text-emerald-600 mt-0.5">+{pct}%</p>
            </div>
          ))}
        </div>
      )}

      {/* Metrics Row */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-800/40 text-xs text-slate-500">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <BarChart3 size={11} />
            Vol: <span className="text-slate-300 font-mono">{signal.volume_ratio.toFixed(1)}x</span>
          </span>
          <span className="flex items-center gap-1">
            ATH: <span className="text-slate-300 font-mono">{formatPct(signal.ath_distance_pct, true)}</span>
          </span>
          <span className="flex items-center gap-1">
            RR: <span className="text-slate-300 font-mono">1:{signal.reward_risk_ratio.toFixed(1)}</span>
          </span>
        </div>
        {signal.breakout_date && (
          <span className="flex items-center gap-1">
            <Clock size={10} />
            Breakout {signal.breakout_date}
          </span>
        )}
      </div>

      {/* Action Row */}
      <div className="mt-4">
        <Button 
          variant="primary" 
          size="sm" 
          className="w-full font-bold"
          onClick={(e: React.MouseEvent) => {
            e.preventDefault();
            mutate();
          }}
          disabled={isPending}
        >
          {isPending ? "Executing..." : "Enter Paper Trade"}
        </Button>
      </div>
    </Card>
  );
}

"use client";

import { useState } from "react";
import {
  SectionHeader,
  StatCard,
  Card,
  CardHeader,
  CardTitle,
  Badge,
  Button,
  EmptyState,
  Spinner,
} from "@/components/ui";
import {
  formatCurrency,
  formatPct,
  getPnlColor,
  getPnlBg,
  getStatusColor,
  cn,
  formatDateTime,
  timeAgo,
  calculatePositionSize,
} from "@/lib/utils";
import {
  Briefcase,
  TrendingUp,
  TrendingDown,
  Plus,
  X,
  DollarSign,
  Shield,
  Target,
  Activity,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import type { PaperTrade } from "@/lib/api";

// Live API data will replace DEMO_TRADES

function TradeRow({ trade }: { trade: PaperTrade }) {
  const pnl = trade.unrealized_pnl + trade.realized_pnl;
  const isOpen = trade.status === "OPEN";

  return (
    <div className={cn(
      "rounded-xl border p-4 transition-all",
      isOpen ? "border-slate-800/60 bg-slate-900/40" : "border-slate-800/30 bg-slate-900/20"
    )}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-white font-mono">{trade.symbol}</span>
            <span className={cn(
              "text-xs px-2 py-0.5 rounded-full border font-medium",
              getStatusColor(trade.status)
            )}>
              {trade.status.replace("_", " ")}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            {trade.strategy_id?.replace(/_/g, " ").toUpperCase() || "UNKNOWN"} • {trade.qty} shares • Opened {timeAgo(trade.opened_at)}
          </p>
        </div>
        <div className={cn(
          "text-right px-3 py-1.5 rounded-lg border",
          getPnlBg(pnl)
        )}>
          <p className={cn("text-sm font-bold font-mono", getPnlColor(pnl))}>
            {pnl >= 0 ? "+" : ""}{formatCurrency(pnl)}
          </p>
          <p className={cn("text-xs font-medium", getPnlColor(pnl))}>
            {formatPct(trade.pnl_pct, true)}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center">
        <div>
          <p className="text-[10px] text-slate-600">Entry</p>
          <p className="text-xs font-bold text-white font-mono">{formatCurrency(trade.entry_price)}</p>
        </div>
        <div>
          <p className="text-[10px] text-slate-600">Current</p>
          <p className={cn(
            "text-xs font-bold font-mono",
            trade.current_price && trade.current_price > trade.entry_price ? "text-emerald-400" : "text-red-400"
          )}>
            {trade.current_price ? formatCurrency(trade.current_price) : "—"}
          </p>
        </div>
        <div>
          <p className="text-[10px] text-slate-600">Stop Loss</p>
          <p className="text-xs font-bold text-red-400 font-mono">{formatCurrency(trade.stop_loss)}</p>
        </div>
        <div>
          <p className="text-[10px] text-slate-600">TP1 / TP2 / TP3</p>
          <p className="text-xs font-bold text-emerald-400 font-mono truncate">
            {trade.targets.map(t => formatCurrency(t, 0)).join(" · ")}
          </p>
        </div>
      </div>

      {/* SL Trailing Indicators */}
      {isOpen && (
        <div className="flex items-center gap-3 mt-3 pt-3 border-t border-slate-800/40">
          <div className={cn(
            "flex items-center gap-1 text-[10px] font-medium",
            trade.sl_moved_to_entry ? "text-teal-400" : "text-slate-600"
          )}>
            {trade.sl_moved_to_entry
              ? <CheckCircle2 size={11} />
              : <AlertCircle size={11} />}
            SL → Entry
          </div>
          <div className={cn(
            "flex items-center gap-1 text-[10px] font-medium",
            trade.sl_moved_to_tp1 ? "text-teal-400" : "text-slate-600"
          )}>
            {trade.sl_moved_to_tp1
              ? <CheckCircle2 size={11} />
              : <AlertCircle size={11} />}
            SL → TP1
          </div>
          <div className="ml-auto text-[10px] text-slate-500">
            Risk: {formatCurrency(trade.risk_amount)} ({formatPct(trade.risk_pct)})
          </div>
        </div>
      )}
    </div>
  );
}

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function PaperTradingPage() {
  const [activeTab, setActiveTab] = useState<"open" | "closed">("open");
  
  // Calculator state
  const [capital, setCapital] = useState<string>("100000");
  const [riskPct, setRiskPct] = useState<string>("2");
  const [entry, setEntry] = useState<string>("");
  const [sl, setSl] = useState<string>("");

  const { data: trades, isLoading } = useQuery({
    queryKey: ["paperTrades"],
    queryFn: api.paperTrades.list,
    refetchInterval: 10000,
  });

  const allTrades = trades || [];
  const openTrades = allTrades.filter(t => t.status === "OPEN");
  const closedTrades = allTrades.filter(t => t.status !== "OPEN");

  const totalPnl = allTrades.reduce((sum, t) => sum + (t.unrealized_pnl || 0) + (t.realized_pnl || 0), 0);
  const realizedPnl = closedTrades.reduce((sum, t) => sum + (t.realized_pnl || 0), 0);
  const unrealizedPnl = openTrades.reduce((sum, t) => sum + (t.unrealized_pnl || 0), 0);
  const winRate = closedTrades.length > 0
    ? (closedTrades.filter(t => t.realized_pnl > 0).length / closedTrades.length * 100).toFixed(0)
    : "—";
    
  let recommendedSize = 0;
  const c = parseFloat(capital);
  const r = parseFloat(riskPct);
  const e = parseFloat(entry);
  const s = parseFloat(sl);
  
  if (c > 0 && r > 0 && e > 0 && s > 0 && e > s) {
    const riskAmount = c * (r / 100);
    const riskPerShare = e - s;
    recommendedSize = Math.floor(riskAmount / riskPerShare);
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Paper Trading</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Simulated trades with full P&L tracking — no real money
          </p>
        </div>
        <Button variant="primary" size="sm" icon={<Plus size={13} />}>
          New Trade
        </Button>
      </div>

      {/* P&L Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard
          label="Total P&L"
          value={`${totalPnl >= 0 ? "+" : ""}${formatCurrency(totalPnl, 0)}`}
          sub="Realized + Unrealized"
          icon={<Activity size={18} />}
          trend={totalPnl >= 0 ? "up" : "down"}
        />
        <StatCard
          label="Realized P&L"
          value={`${realizedPnl >= 0 ? "+" : ""}${formatCurrency(realizedPnl, 0)}`}
          sub="Closed trades"
          icon={<CheckCircle2 size={18} />}
          trend={realizedPnl >= 0 ? "up" : "down"}
        />
        <StatCard
          label="Unrealized P&L"
          value={`${unrealizedPnl >= 0 ? "+" : ""}${formatCurrency(unrealizedPnl, 0)}`}
          sub="Open positions"
          icon={<TrendingUp size={18} />}
          trend={unrealizedPnl >= 0 ? "up" : "down"}
        />
        <StatCard
          label="Win Rate"
          value={`${winRate}%`}
          sub={`${closedTrades.length} closed trades`}
          icon={<Target size={18} />}
          trend={Number(winRate) >= 50 ? "up" : "down"}
        />
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 bg-slate-900 rounded-xl border border-slate-800 p-1 w-fit">
        {(["open", "closed"] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-all",
              activeTab === tab
                ? "bg-teal-500/20 text-teal-400 border border-teal-500/30"
                : "text-slate-500 hover:text-slate-300"
            )}
          >
            {tab === "open" ? `Open (${openTrades.length})` : `Closed (${closedTrades.length})`}
          </button>
        ))}
      </div>

      {/* Trade List */}
      <div className="space-y-3">
        {isLoading ? (
          <Spinner />
        ) : (activeTab === "open" ? openTrades : closedTrades).length === 0 ? (
          <EmptyState
            icon={<Briefcase size={32} />}
            title={activeTab === "open" ? "No open positions" : "No closed trades"}
            description={activeTab === "open"
              ? "Open a paper trade from an active signal to start tracking."
              : "Closed trades will appear here after you exit positions."
            }
          />
        ) : (
          (activeTab === "open" ? openTrades : closedTrades).map(trade => (
            <TradeRow key={trade._id} trade={trade} />
          ))
        )}
      </div>

      {/* Position Calculator */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign size={16} className="text-teal-400" />
            Position Size Calculator
          </CardTitle>
        </CardHeader>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div key="Capital">
              <label className="text-xs text-slate-500 mb-1.5 block">Capital</label>
              <input
                type="number"
                value={capital}
                onChange={(e) => setCapital(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-teal-500/50"
              />
            </div>
            <div key="Risk%">
              <label className="text-xs text-slate-500 mb-1.5 block">Risk %</label>
              <input
                type="number"
                value={riskPct}
                onChange={(e) => setRiskPct(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-teal-500/50"
              />
            </div>
            <div key="Entry Price">
              <label className="text-xs text-slate-500 mb-1.5 block">Entry Price</label>
              <input
                type="number"
                value={entry}
                onChange={(e) => setEntry(e.target.value)}
                placeholder="1250"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-teal-500/50"
              />
            </div>
            <div key="Stop Loss">
              <label className="text-xs text-slate-500 mb-1.5 block">Stop Loss</label>
              <input
                type="number"
                value={sl}
                onChange={(e) => setSl(e.target.value)}
                placeholder="1140"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-teal-500/50"
              />
            </div>
        </div>
        <div className="mt-4 p-3 bg-teal-500/5 border border-teal-500/20 rounded-lg">
          <p className="text-xs text-slate-500 mb-1">Recommended Position Size</p>
          <p className="text-xl font-bold text-teal-400 font-mono">
            {recommendedSize > 0 ? `${recommendedSize} shares` : "Calculate above →"}
          </p>
        </div>
      </Card>
    </div>
  );
}

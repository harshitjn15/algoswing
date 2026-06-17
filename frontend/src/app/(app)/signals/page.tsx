"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  SectionHeader,
  Button,
  Badge,
  Spinner,
  EmptyState,
  Card,
} from "@/components/ui";
import { SignalCard } from "@/components/trading/signal-card";
import {
  TrendingUp,
  RefreshCw,
  Filter,
  Zap,
  Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";

type FilterType = "all" | "today" | "recent";
type ConfidenceFilter = "ALL" | "HIGH" | "MEDIUM" | "LOW";

export default function SignalsPage() {
  const queryClient = useQueryClient();
  const [isScanning, setIsScanning] = useState(false);
  const [filter, setFilter] = useState<FilterType>("all");
  const [confidence, setConfidence] = useState<ConfidenceFilter>("ALL");

  const { data: allSignals, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["signals", "list"],
    queryFn: () => api.signals.list(100),
    refetchInterval: 60_000,
  });

  const { data: todaySignals } = useQuery({
    queryKey: ["signals", "today"],
    queryFn: api.signals.today,
  });

  const { data: recentSignals } = useQuery({
    queryKey: ["signals", "recent"],
    queryFn: () => api.signals.recent(7),
  });

  const sourceMap: Record<FilterType, typeof allSignals> = {
    all:    allSignals,
    today:  todaySignals,
    recent: recentSignals,
  };

  const raw = sourceMap[filter] ?? [];
  const signals = confidence === "ALL"
    ? raw
    : raw.filter(s => s.confidence === confidence);

  const filters: Array<{ key: FilterType; label: string; icon: React.ElementType; count?: number }> = [
    { key: "all",    label: "Active",  icon: TrendingUp, count: allSignals?.length },
    { key: "today",  label: "Today",   icon: Zap,        count: todaySignals?.length },
    { key: "recent", label: "7 Days",  icon: Clock,      count: recentSignals?.length },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Signals</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            IPO ATH Retest trade setups with entry, SL, and targets
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          icon={<RefreshCw size={13} className={isFetching || isScanning ? "animate-spin" : ""} />}
          disabled={isScanning}
          onClick={async () => {
            setIsScanning(true);
            try {
              await api.scanner.runSync();
              await queryClient.invalidateQueries();
            } finally {
              setIsScanning(false);
            }
          }}
        >
          {isScanning ? "Scanning..." : "Refresh"}
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Time Filter */}
        <div className="flex items-center bg-slate-900 rounded-xl border border-slate-800 p-1 gap-1">
          {filters.map(({ key, label, icon: Icon, count }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
                filter === key
                  ? "bg-teal-500/20 text-teal-400 border border-teal-500/30"
                  : "text-slate-500 hover:text-slate-300"
              )}
            >
              <Icon size={12} />
              {label}
              {count !== undefined && (
                <span className={cn(
                  "px-1.5 py-0.5 rounded-full text-[10px]",
                  filter === key ? "bg-teal-500/30 text-teal-400" : "bg-slate-800 text-slate-500"
                )}>
                  {count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Confidence Filter */}
        <div className="flex items-center gap-1.5">
          <Filter size={13} className="text-slate-500" />
          {(["ALL", "HIGH", "MEDIUM", "LOW"] as ConfidenceFilter[]).map(c => (
            <button
              key={c}
              onClick={() => setConfidence(c)}
              className={cn(
                "px-2.5 py-1 rounded-lg text-xs font-medium border transition-all",
                confidence === c
                  ? c === "HIGH"   ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                  : c === "MEDIUM" ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
                  : c === "LOW"    ? "bg-slate-500/20 text-slate-400 border-slate-500/30"
                  :                  "bg-teal-500/20 text-teal-400 border-teal-500/30"
                  : "bg-transparent text-slate-600 border-slate-800 hover:text-slate-400"
              )}
            >
              {c}
            </button>
          ))}
        </div>

        {signals.length > 0 && (
          <span className="text-xs text-slate-500 ml-auto">
            {signals.length} signal{signals.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      {/* Signals Grid */}
      {isLoading ? (
        <Spinner />
      ) : signals.length === 0 ? (
        <EmptyState
          icon={<TrendingUp size={32} />}
          title="No signals found"
          description="Try changing filters or trigger a manual scanner run to look for new setups."
          action={
            <Button
              variant="primary"
              size="sm"
              icon={<Zap size={13} />}
              onClick={async () => {
                setIsScanning(true);
                try {
                  await api.scanner.runSync();
                  await queryClient.invalidateQueries();
                } finally {
                  setIsScanning(false);
                }
              }}
              disabled={isScanning}
            >
              {isScanning ? "Scanning..." : "Trigger Scanner"}
            </Button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {signals.map(signal => (
            <SignalCard key={signal._id} signal={signal} />
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

import { useQuery } from "@tanstack/react-query";
import { api, Signal, WatchlistEntry } from "@/lib/api";
import {
  formatCurrency,
  formatPct,
  getPnlColor,
  timeAgo,
  getConfidenceBg,
  getStatusColor,
} from "@/lib/utils";
import {
  StatCard,
  Card,
  CardHeader,
  CardTitle,
  Badge,
  Spinner,
  EmptyState,
  Button,
  LiveDot,
  SectionHeader,
} from "@/components/ui";
import { SignalCard } from "@/components/trading/signal-card";
import { WatchlistRow } from "@/components/trading/watchlist-row";
import {
  TrendingUp,
  BookOpen,
  Activity,
  Zap,
  RefreshCw,
  AlertTriangle,
  BarChart2,
  Clock,
  Target,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { useQueryClient } from "@tanstack/react-query";

// Live Equity Data from Backend

// ── Custom Tooltip ─────────────────────────────────────────
function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-panel rounded-xl px-4 py-3 shadow-xl shadow-black/50">
      <p className="text-xs text-slate-400 mb-1.5 uppercase tracking-wider">{label}</p>
      <p className="text-base font-bold text-teal-400 font-mono">
        {formatCurrency(payload[0].value, 0)}
      </p>
    </div>
  );
}

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const {
    data: signals,
    isLoading: signalsLoading,
    refetch: refetchSignals,
    isFetching,
  } = useQuery({
    queryKey: ["signals", "active"],
    queryFn: () => api.signals.list(10),
    refetchInterval: 60_000,
  });

  const { data: watchlistStats } = useQuery({
    queryKey: ["watchlist", "stats"],
    queryFn: api.watchlist.stats,
  });

  const { data: nearAth } = useQuery({
    queryKey: ["watchlist", "near-ath"],
    queryFn: api.watchlist.nearAth,
  });

  const { data: scannerStatus } = useQuery({
    queryKey: ["scanner", "status"],
    queryFn: api.scanner.status,
    refetchInterval: 30_000,
  });

  const { data: todaySignals } = useQuery({
    queryKey: ["signals", "today"],
    queryFn: api.signals.today,
  });

  const { data: equityDataRaw } = useQuery({
    queryKey: ["equity"],
    queryFn: api.paperTrades.equity,
  });

  const equityData = equityDataRaw || [];

  const activeSignals = signals?.filter(s => s.status === "ACTIVE") ?? [];
  const totalNearAth = watchlistStats?.near_ath ?? 0;
  const marketOpen = scannerStatus?.market_open ?? false;
  const todayCount = todaySignals?.length ?? 0;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-slate-500 mt-0.5 flex items-center gap-2">
            <LiveDot live={marketOpen} />
            {marketOpen ? "Market Open — Scanner Active" : "Market Closed"}
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          icon={<RefreshCw size={13} className={isFetching ? "animate-spin" : ""} />}
          onClick={() => {
            queryClient.invalidateQueries();
          }}
        >
          Refresh
        </Button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard
          label="Active Signals"
          value={activeSignals.length}
          sub="Live opportunities"
          icon={<TrendingUp size={18} />}
          trend={activeSignals.length > 0 ? "up" : "neutral"}
        />
        <StatCard
          label="Today's Signals"
          value={todayCount}
          sub="Generated today"
          icon={<Zap size={18} />}
        />
        <StatCard
          label="Near ATH"
          value={totalNearAth}
          sub={`of ${watchlistStats?.total ?? 0} watched`}
          icon={<Target size={18} />}
        />
        <StatCard
          label="Scanner"
          value={marketOpen ? "LIVE" : "CLOSED"}
          sub={scannerStatus?.jobs?.[0]?.next_run
            ? `Next: ${new Date(scannerStatus.jobs[0].next_run).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}`
            : "Scheduled"
          }
          icon={<Activity size={18} />}
          trend={marketOpen ? "up" : "neutral"}
        />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">

        {/* Equity Curve (placeholder) */}
        <div className="xl:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart2 size={16} className="text-teal-400" />
                Portfolio Performance
              </CardTitle>
              <Badge variant="muted" size="sm">Paper Trading</Badge>
            </CardHeader>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={equityData} margin={{ top: 4, right: 8, bottom: 0, left: 8 }}>
                <defs>
                  <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#14b8a6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#14b8a6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222 30% 16%)" />
                <XAxis
                  dataKey="date"
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  interval={4}
                />
                <YAxis
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
                  width={48}
                />
                <Tooltip content={<ChartTooltip />} />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#14b8a6"
                  strokeWidth={2}
                  fill="url(#colorVal)"
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Market Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity size={16} className="text-teal-400" />
              Market Summary
            </CardTitle>
          </CardHeader>
          <div className="space-y-3">
            {[
              { label: "Watchlist Size", value: watchlistStats?.total ?? 0, unit: "stocks" },
              { label: "Near ATH", value: totalNearAth, unit: "qualifying" },
              { label: "ATH Coverage", value: `${watchlistStats?.pct_near_ath ?? 0}%`, unit: "of watchlist" },
              { label: "Today's Signals", value: todayCount, unit: "generated" },
            ].map(({ label, value, unit }) => (
              <div key={label} className="flex items-center justify-between py-2.5 border-b border-white/[0.05] last:border-0 hover:bg-white/[0.02] px-2 rounded-lg transition-colors">
                <span className="text-xs text-slate-400 font-medium">{label}</span>
                <div className="text-right">
                  <span className="text-sm font-bold text-white font-mono">{value}</span>
                  <span className="text-xs text-slate-500 ml-1.5">{unit}</span>
                </div>
              </div>
            ))}
            <div className="pt-2">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Clock size={12} />
                Scanner interval: every 30 min
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Active Signals */}
      <div>
        <SectionHeader
          title="Active Signals"
          subtitle={`${activeSignals.length} live opportunities`}
          action={
            <Button variant="ghost" size="sm" icon={<TrendingUp size={13} />}>
              View All
            </Button>
          }
        />

        {signalsLoading ? (
          <Spinner />
        ) : activeSignals.length === 0 ? (
          <EmptyState
            icon={<TrendingUp size={32} />}
            title="No active signals"
            description="Signals appear here when the scanner detects IPO ATH Retest setups during market hours."
            action={
              <Button
                variant="primary"
                size="sm"
                icon={<RefreshCw size={13} />}
                onClick={() => refetchSignals()}
              >
                Run Scanner
              </Button>
            }
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {activeSignals.slice(0, 6).map((signal) => (
              <SignalCard key={signal._id} signal={signal} />
            ))}
          </div>
        )}
      </div>

      {/* Near ATH Watchlist Preview */}
      {(nearAth?.length ?? 0) > 0 && (
        <div>
          <SectionHeader
            title="Near ATH Stocks"
            subtitle="Stocks approaching all-time highs"
          />
          <div className="space-y-2">
            {nearAth?.slice(0, 5).map((entry) => (
              <WatchlistRow key={entry.symbol} entry={entry} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

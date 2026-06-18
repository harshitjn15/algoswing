"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  SectionHeader,
  Button,
  StatCard,
  Spinner,
  EmptyState,
  Card,
  LiveDot,
} from "@/components/ui";
import { WatchlistRow } from "@/components/trading/watchlist-row";
import {
  BookOpen,
  RefreshCw,
  TrendingUp,
  BarChart3,
  Target,
  Zap,
  Search,
  ChevronUp,
  ChevronDown,
} from "lucide-react";

type SortField = "symbol" | "last_close" | "ath" | "ath_distance_pct" | "volume_ratio";

export default function WatchlistPage() {
  const queryClient = useQueryClient();
  const [nearAthOnly, setNearAthOnly] = useState(true);
  const [search, setSearch] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  
  const [sortField, setSortField] = useState<SortField>("ath_distance_pct");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder(field === "symbol" ? "asc" : "desc");
    }
  };

  const { data: entries, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["watchlist", nearAthOnly],
    queryFn: () => api.watchlist.list(nearAthOnly),
    refetchInterval: 60_000,
  });

  const { data: stats } = useQuery({
    queryKey: ["watchlist", "stats"],
    queryFn: api.watchlist.stats,
  });

  const { data: scannerStatus } = useQuery({
    queryKey: ["scanner", "status"],
    queryFn: api.scanner.status,
    refetchInterval: 30_000,
  });

  const marketOpen = scannerStatus?.market_open ?? false;
  const lastScanned = entries?.[0]?.updated_at;
  const lastScannedFormatted = lastScanned 
    ? new Date(lastScanned + "Z").toLocaleString() 
    : "Unknown";

  const filtered = (entries ?? []).filter(e =>
    e.symbol.toLowerCase().includes(search.toLowerCase())
  );

  const sorted = [...filtered].sort((a, b) => {
    let valA = a[sortField];
    let valB = b[sortField];
    if (valA === undefined || valA === null) valA = sortField === "symbol" ? "" : 0;
    if (valB === undefined || valB === null) valB = sortField === "symbol" ? "" : 0;
    
    if (valA < valB) return sortOrder === "asc" ? -1 : 1;
    if (valA > valB) return sortOrder === "asc" ? 1 : -1;
    return 0;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-white">Watchlist</h1>
            <LiveDot live={marketOpen} />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            IPO Base Scan stocks with ATH distance and volume metrics
          </p>
          <p className="text-xs text-slate-500 mt-1 flex items-center gap-1.5">
            <Zap size={11} className={marketOpen ? "text-teal-500" : "text-slate-500"} />
            Last Scan: <span className="font-mono">{lastScannedFormatted}</span>
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

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
        <StatCard
          label="Total Watched"
          value={stats?.total ?? 0}
          sub="From IPO Base Scan"
          icon={<BookOpen size={18} />}
        />
        <StatCard
          label="Near ATH"
          value={stats?.near_ath ?? 0}
          sub="Within ±5% of high"
          icon={<Target size={18} />}
          trend="up"
        />
        <StatCard
          label="ATH Coverage"
          value={`${stats?.pct_near_ath ?? 0}%`}
          sub="Qualify for strategy"
          icon={<BarChart3 size={18} />}
          className="hidden lg:block"
        />
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search symbol..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-teal-500/50 focus:ring-1 focus:ring-teal-500/20 transition-colors"
          />
        </div>

        {/* Near ATH Toggle */}
        <button
          onClick={() => setNearAthOnly(!nearAthOnly)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-all ${
            nearAthOnly
              ? "bg-teal-500/20 text-teal-400 border-teal-500/30"
              : "bg-slate-900 text-slate-500 border-slate-800 hover:text-slate-300"
          }`}
        >
          <Target size={14} />
          Near ATH Only
        </button>

        <span className="text-xs text-slate-500 ml-auto">
          {filtered.length} stocks
        </span>
      </div>

      {/* Table Header */}
      <div className="hidden md:flex items-center px-4 py-2 text-[10px] text-slate-500 uppercase tracking-wider font-medium">
        <div 
          className="flex-[2] min-w-[100px] flex items-center gap-1 cursor-pointer hover:text-white select-none transition-colors" 
          onClick={() => handleSort("symbol")}
        >
          Symbol {sortField === "symbol" && (sortOrder === "asc" ? <ChevronUp size={12}/> : <ChevronDown size={12}/>)}
        </div>
        <div 
          className="flex-1 text-right hidden sm:flex justify-end items-center gap-1 cursor-pointer hover:text-white select-none transition-colors"
          onClick={() => handleSort("last_close")}
        >
          {sortField === "last_close" && (sortOrder === "asc" ? <ChevronUp size={12}/> : <ChevronDown size={12}/>)} {marketOpen ? "Live Price" : "Last Close"}
        </div>
        <div 
          className="flex-1 text-right hidden md:flex justify-end items-center gap-1 cursor-pointer hover:text-white select-none transition-colors"
          onClick={() => handleSort("ath")}
        >
          {sortField === "ath" && (sortOrder === "asc" ? <ChevronUp size={12}/> : <ChevronDown size={12}/>)} ATH
        </div>
        <div 
          className="flex-1 text-right flex justify-end items-center gap-1 cursor-pointer hover:text-white select-none transition-colors"
          onClick={() => handleSort("ath_distance_pct")}
        >
          {sortField === "ath_distance_pct" && (sortOrder === "asc" ? <ChevronUp size={12}/> : <ChevronDown size={12}/>)} ATH Dist
        </div>
        <div 
          className="flex-1 text-right hidden sm:flex justify-end items-center gap-1 cursor-pointer hover:text-white select-none transition-colors"
          onClick={() => handleSort("volume_ratio")}
        >
          {sortField === "volume_ratio" && (sortOrder === "asc" ? <ChevronUp size={12}/> : <ChevronDown size={12}/>)} Vol Ratio
        </div>
        <div className="flex-1 hidden lg:block"></div>
      </div>

      {/* Rows */}
      {isLoading ? (
        <Spinner />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<BookOpen size={32} />}
          title="No stocks in watchlist"
          description="Run the scanner to populate the watchlist from Chartink IPO Base Scan."
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
              {isScanning ? "Scanning..." : "Run Scanner"}
            </Button>
          }
        />
      ) : (
        <div className="space-y-2">
          {sorted.map(entry => (
            <WatchlistRow key={entry.symbol} entry={entry} marketOpen={marketOpen} />
          ))}
        </div>
      )}
    </div>
  );
}

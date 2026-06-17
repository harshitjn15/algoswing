// ─── API Client ──────────────────────────────────────────
// All calls go through this base client pointing at the FastAPI backend.

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function fetcher<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}/api/v1${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    let errorMsg = `API error: ${res.status}`;
    try {
      const errorJson = await res.clone().json();
      errorMsg = errorJson.detail || JSON.stringify(errorJson) || errorMsg;
    } catch {
      const errorText = await res.text();
      errorMsg = errorText || errorMsg;
    }
    console.error(`[API Error] ${path}:`, errorMsg);
    throw new Error(errorMsg);
  }

  return res.json() as Promise<T>;
}

// ─── Types ────────────────────────────────────────────────

export type SignalStatus =
  | "ACTIVE" | "TRIGGERED" | "EXPIRED" | "SL_HIT"
  | "TP1_HIT" | "TP2_HIT" | "TP3_HIT" | "CLOSED";

export type ConfidenceLevel = "HIGH" | "MEDIUM" | "LOW";

export interface Signal {
  _id: string;
  symbol: string;
  exchange: string;
  strategy_id: string;
  isin?: string;
  entry: number;
  stop_loss: number;
  targets: number[];
  risk_pct: number;
  reward_risk_ratio: number;
  ath: number;
  ath_date?: string;
  ath_distance_pct: number;
  breakout_date?: string;
  breakout_price?: number;
  volume_ratio: number;
  avg_volume_20d?: number;
  confidence: ConfidenceLevel;
  status: SignalStatus;
  notes?: string;
  generated_at: string;
}

export interface WatchlistEntry {
  _id?: string;
  symbol: string;
  exchange: string;
  isin?: string;
  scanner: string;
  listing_date?: string;
  ath?: number;
  ath_date?: string;
  last_close?: number;
  ath_distance_pct?: number;
  near_ath: boolean;
  volume_ratio?: number;
  avg_volume_20d?: number;
  scanned_at: string;
  updated_at: string;
}

export interface PaperTrade {
  _id?: string;
  signal_id?: string;
  user_id: string;
  symbol: string;
  exchange: string;
  direction: "LONG" | "SHORT";
  strategy_id: string;
  entry_price: number;
  qty: number;
  position_value: number;
  stop_loss: number;
  targets: number[];
  risk_amount: number;
  risk_pct: number;
  current_price?: number;
  realized_pnl: number;
  unrealized_pnl: number;
  pnl_pct: number;
  status: "OPEN" | "CLOSED" | "SL_HIT" | "TP1_HIT" | "TP2_HIT" | "TP3_HIT" | "PARTIAL" | "CANCELLED";
  sl_moved_to_entry: boolean;
  sl_moved_to_tp1: boolean;
  exit_price?: number;
  exit_reason?: string;
  opened_at: string;
  closed_at?: string;
}

export interface WatchlistStats {
  total: number;
  near_ath: number;
  pct_near_ath: number;
}

export interface ScannerStatus {
  running: boolean;
  market_open: boolean;
  jobs: Array<{ id: string; name: string; next_run: string | null }>;
}

export interface HealthStatus {
  status: string;
  app: string;
  version: string;
  services?: {
    mongodb?: { status: string };
    telegram?: { status: string; connected?: boolean; bot_name?: string };
  };
}

export interface Strategy {
  id: string;
  name: string;
  version: string;
  description: string;
}

// ─── API Functions ────────────────────────────────────────

export const api = {
  // Signals
  signals: {
    list: (limit = 50) =>
      fetcher<Signal[]>(`/signals?limit=${limit}`),
    today: () =>
      fetcher<Signal[]>("/signals/today"),
    recent: (days = 7) =>
      fetcher<Signal[]>(`/signals/recent?days=${days}`),
    get: (id: string) =>
      fetcher<Signal>(`/signals/${id}`),
  },

  // Watchlist
  watchlist: {
    list: (nearAthOnly = false) =>
      fetcher<WatchlistEntry[]>(`/watchlist?near_ath_only=${nearAthOnly}`),
    nearAth: () =>
      fetcher<WatchlistEntry[]>("/watchlist/near-ath"),
    stats: () =>
      fetcher<WatchlistStats>("/watchlist/stats"),
    get: (symbol: string) =>
      fetcher<WatchlistEntry>(`/watchlist/${symbol}`),
  },

  // Scanner
  scanner: {
    run: () =>
      fetcher<{ message: string; market_open: boolean }>("/scanner/run", { method: "POST" }),
    runSync: () =>
      fetcher<{ message: string }>("/scanner/run-sync", { method: "POST" }),
    status: () =>
      fetcher<ScannerStatus>("/scanner/status"),
    strategies: () =>
      fetcher<Strategy[]>("/scanner/strategies"),
  },

  // Health
  health: {
    check: () => fetcher<HealthStatus>("/health"),
    detailed: () => fetcher<HealthStatus>("/health/detailed"),
  },

  // Paper Trading
  paperTrades: {
    list: () => fetcher<PaperTrade[]>("/paper-trading"),
    create: (data: Partial<PaperTrade>) => 
      fetcher<PaperTrade>("/paper-trading", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    close: (id: string, data: { exit_price: number; exit_reason: string }) =>
      fetcher<{ message: string; pnl: number; pnl_pct: number }>(`/paper-trading/${id}/close`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    equity: () =>
      fetcher<{ date: string; value: number }[]>("/paper-trading/equity"),
  },
};

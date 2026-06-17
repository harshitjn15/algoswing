import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Signal, WatchlistEntry } from "./api";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ─── Number formatters ────────────────────────────────────

export function formatCurrency(value: number, decimals = 2): string {
  return `₹${value.toLocaleString("en-IN", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
}

export function formatPct(value: number, showSign = false): string {
  const sign = showSign && value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function formatVolume(value: number): string {
  if (value >= 1_00_00_000) return `${(value / 1_00_00_000).toFixed(1)}Cr`;
  if (value >= 1_00_000) return `${(value / 1_00_000).toFixed(1)}L`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toFixed(0);
}

export function formatNumber(value: number): string {
  return value.toLocaleString("en-IN");
}

// ─── Date formatters ──────────────────────────────────────

export function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function formatDateTime(isoString: string): string {
  return new Date(isoString).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function timeAgo(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// ─── Signal helpers ───────────────────────────────────────

export function getConfidenceColor(confidence: string): string {
  switch (confidence) {
    case "HIGH":   return "text-emerald-400";
    case "MEDIUM": return "text-amber-400";
    default:       return "text-slate-400";
  }
}

export function getConfidenceBg(confidence: string): string {
  switch (confidence) {
    case "HIGH":   return "bg-emerald-400/10 text-emerald-400 border-emerald-400/20";
    case "MEDIUM": return "bg-amber-400/10 text-amber-400 border-amber-400/20";
    default:       return "bg-slate-400/10 text-slate-400 border-slate-400/20";
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "ACTIVE":    return "bg-teal-500/10 text-teal-400 border-teal-500/20";
    case "TRIGGERED": return "bg-blue-500/10 text-blue-400 border-blue-500/20";
    case "SL_HIT":    return "bg-red-500/10 text-red-400 border-red-500/20";
    case "TP3_HIT":
    case "CLOSED":    return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    default:          return "bg-slate-500/10 text-slate-400 border-slate-500/20";
  }
}

export function getPnlColor(pnl: number): string {
  return pnl >= 0 ? "text-emerald-400" : "text-red-400";
}

export function getPnlBg(pnl: number): string {
  return pnl >= 0
    ? "bg-emerald-400/10 border-emerald-400/20"
    : "bg-red-400/10 border-red-400/20";
}

// ─── Trade calculations ───────────────────────────────────

export function calculatePositionSize(
  capital: number,
  riskPct: number,
  entry: number,
  stopLoss: number
): number {
  const riskAmount = capital * (riskPct / 100);
  const slDistance = Math.abs(entry - stopLoss);
  if (slDistance === 0) return 0;
  return Math.floor(riskAmount / slDistance);
}

export function calculateRiskAmount(
  entry: number,
  stopLoss: number,
  qty: number
): number {
  return Math.abs(entry - stopLoss) * qty;
}

export function calculateUnrealizedPnl(
  entry: number,
  current: number,
  qty: number
): number {
  return (current - entry) * qty;
}

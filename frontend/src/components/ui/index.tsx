"use client";

import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

// ─── Card ─────────────────────────────────────────────────
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
}

export function Card({ className, hover, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "glass rounded-2xl p-5 relative overflow-hidden transition-all duration-300",
        hover && "card-hover cursor-pointer",
        className
      )}
      {...props}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent pointer-events-none" />
      <div className="relative z-10">{children}</div>
    </div>
  );
}

export function CardHeader({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("flex items-center justify-between mb-4", className)} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ className, children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn("text-sm font-semibold text-slate-300", className)} {...props}>
      {children}
    </h3>
  );
}

// ─── Badge ────────────────────────────────────────────────
interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "profit" | "loss" | "warning" | "info" | "muted";
  size?: "sm" | "md";
}

const badgeVariants: Record<string, string> = {
  default: "bg-teal-400/10 text-teal-400 border-teal-400/20",
  profit:  "bg-emerald-400/10 text-emerald-400 border-emerald-400/20",
  loss:    "bg-red-400/10 text-red-400 border-red-400/20",
  warning: "bg-amber-400/10 text-amber-400 border-amber-400/20",
  info:    "bg-blue-400/10 text-blue-400 border-blue-400/20",
  muted:   "bg-slate-700/40 text-slate-400 border-slate-700/40",
};

export function Badge({ className, variant = "default", size = "sm", children, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center border font-medium rounded-full",
        size === "sm" ? "text-xs px-2 py-0.5" : "text-sm px-3 py-1",
        badgeVariants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

// ─── Button ───────────────────────────────────────────────
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: React.ReactNode;
}

const buttonVariants: Record<string, string> = {
  primary:   "bg-gradient-to-r from-teal-500 to-teal-400 hover:from-teal-400 hover:to-teal-300 text-teal-950 font-bold shadow-[0_0_20px_rgba(20,184,166,0.3)] hover:shadow-[0_0_30px_rgba(20,184,166,0.5)] border-t border-teal-300/30",
  secondary: "glass hover:bg-white/[0.05] text-slate-200 shadow-sm",
  ghost:     "hover:bg-white/[0.05] text-slate-400 hover:text-slate-100",
  danger:    "bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.1)]",
};

const buttonSizes: Record<string, string> = {
  sm: "text-xs px-3 py-1.5 rounded-lg",
  md: "text-sm px-4 py-2 rounded-lg",
  lg: "text-sm px-5 py-2.5 rounded-xl",
};

export function Button({
  className,
  variant = "secondary",
  size = "md",
  loading,
  icon,
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center gap-2 font-medium transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed",
        buttonVariants[variant],
        buttonSizes[size],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <Loader2 size={14} className="animate-spin" /> : icon}
      {children}
    </button>
  );
}

// ─── Stat Card ────────────────────────────────────────────
interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon?: React.ReactNode;
  trend?: "up" | "down" | "neutral";
  className?: string;
}

export function StatCard({ label, value, sub, icon, trend, className }: StatCardProps) {
  return (
    <Card className={cn("group", className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">{label}</p>
          <p className={cn(
            "text-2xl font-bold font-mono",
            trend === "up" && "text-emerald-400",
            trend === "down" && "text-red-400",
            !trend && "text-white"
          )}>
            {value}
          </p>
          {sub && <p className="text-xs text-slate-500">{sub}</p>}
        </div>
        {icon && (
          <div className="p-3 rounded-xl glass text-slate-400 group-hover:text-teal-400 group-hover:scale-110 transition-all duration-300 shadow-inner">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}

// ─── Skeleton ────────────────────────────────────────────
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton rounded-lg", className)} />;
}

// ─── Empty State ─────────────────────────────────────────
interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && (
        <div className="mb-4 p-4 rounded-2xl bg-slate-800/50 text-slate-500">
          {icon}
        </div>
      )}
      <h3 className="text-sm font-semibold text-slate-300 mb-1">{title}</h3>
      {description && <p className="text-xs text-slate-500 max-w-xs">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

// ─── Loading Spinner ──────────────────────────────────────
export function Spinner({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center justify-center py-12", className)}>
      <Loader2 size={24} className="animate-spin text-teal-400" />
    </div>
  );
}

// ─── Section Header ──────────────────────────────────────
export function SectionHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <h1 className="text-xl font-bold text-white">{title}</h1>
        {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

// ─── Divider ─────────────────────────────────────────────
export function Divider({ className }: { className?: string }) {
  return <hr className={cn("border-slate-800/60", className)} />;
}

// ─── Live Dot ─────────────────────────────────────────────
export function LiveDot({ live = true }: { live?: boolean }) {
  return (
    <span
      className={cn(
        "inline-block w-2 h-2 rounded-full",
        live ? "bg-teal-400 animate-pulse" : "bg-slate-600"
      )}
    />
  );
}

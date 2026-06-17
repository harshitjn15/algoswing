"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  TrendingUp,
  BookOpen,
  Briefcase,
  BarChart2,
  Link2,
  Settings,
  Zap,
  Menu,
  X,
  ChevronRight,
  Activity,
} from "lucide-react";

const navItems = [
  { href: "/dashboard",     label: "Dashboard",     icon: LayoutDashboard },
  { href: "/signals",       label: "Signals",        icon: TrendingUp },
  { href: "/watchlist",     label: "Watchlist",      icon: BookOpen },
  { href: "/paper-trading", label: "Paper Trading",  icon: Briefcase },
  { href: "/backtesting",   label: "Backtesting",    icon: BarChart2 },
  { href: "/brokers",       label: "Brokers",        icon: Link2 },
  { href: "/strategies",    label: "Strategies",     icon: Zap },
  { href: "/settings",      label: "Settings",       icon: Settings },
];

function NavLink({
  href,
  label,
  icon: Icon,
  active,
  onClick,
}: {
  href: string;
  label: string;
  icon: React.ElementType;
  active: boolean;
  onClick?: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={cn(
        "sidebar-link group",
        active && "active"
      )}
    >
      <Icon
        size={18}
        className={cn(
          "shrink-0 transition-colors",
          active ? "text-teal-400" : "text-slate-500 group-hover:text-slate-300"
        )}
      />
      <span className="truncate">{label}</span>
      {active && (
        <ChevronRight size={14} className="ml-auto text-teal-400 opacity-60" />
      )}
    </Link>
  );
}

// ── Desktop Sidebar ──────────────────────────────────────
export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex w-60 min-h-screen flex-col glass border-r border-slate-800/60 fixed top-0 left-0 z-40">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 py-5 border-b border-slate-800/60">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-cyan-400 flex items-center justify-center glow-primary">
          <Activity size={16} className="text-white" />
        </div>
        <div>
          <p className="font-bold text-sm gradient-text">AlgoSwing</p>
          <p className="text-[10px] text-slate-500">IPO ATH Retest v1.0</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.href}
            {...item}
            active={pathname.startsWith(item.href)}
          />
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-slate-800/60">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
          <span className="text-xs text-slate-500">Market closed</span>
        </div>
      </div>
    </aside>
  );
}

// ── Mobile Bottom Nav ────────────────────────────────────
export function MobileNav() {
  const pathname = usePathname();

  const primaryNav = navItems.slice(0, 5); // Show top 5 in bottom bar

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-50 glass border-t border-slate-800/60 pb-safe">
      <div className="flex items-center justify-around px-2 py-2">
        {primaryNav.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className="flex flex-col items-center gap-1 px-3 py-1 rounded-lg"
            >
              <Icon
                size={20}
                className={cn(
                  "transition-colors",
                  active ? "text-teal-400" : "text-slate-500"
                )}
              />
              <span
                className={cn(
                  "text-[10px] font-medium transition-colors",
                  active ? "text-teal-400" : "text-slate-500"
                )}
              >
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

// ── Mobile Header ─────────────────────────────────────────
export function MobileHeader() {
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();

  return (
    <>
      <header className="lg:hidden sticky top-0 z-50 glass border-b border-slate-800/60 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-gradient-to-br from-teal-500 to-cyan-400 flex items-center justify-center">
            <Activity size={14} className="text-white" />
          </div>
          <span className="font-bold text-sm gradient-text">AlgoSwing</span>
        </div>
        <button
          onClick={() => setMenuOpen(true)}
          className="p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <Menu size={20} className="text-slate-400" />
        </button>
      </header>

      {/* Full-screen mobile menu */}
      {menuOpen && (
        <div className="lg:hidden fixed inset-0 z-[60] glass animate-fade-in">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800/60">
            <span className="font-bold gradient-text">AlgoSwing</span>
            <button
              onClick={() => setMenuOpen(false)}
              className="p-1.5 rounded-lg hover:bg-slate-800"
            >
              <X size={20} className="text-slate-400" />
            </button>
          </div>
          <nav className="px-3 py-4 space-y-0.5">
            {navItems.map((item) => (
              <NavLink
                key={item.href}
                {...item}
                active={pathname.startsWith(item.href)}
                onClick={() => setMenuOpen(false)}
              />
            ))}
          </nav>
        </div>
      )}
    </>
  );
}

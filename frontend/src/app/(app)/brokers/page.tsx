"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { SectionHeader, Card, CardHeader, CardTitle, Badge, StatCard, EmptyState } from "@/components/ui";
import { Link2, CheckCircle2, XCircle, Wifi } from "lucide-react";

export default function BrokersPage() {
  const { data: health } = useQuery({
    queryKey: ["health", "detailed"],
    queryFn: api.health.detailed,
    refetchInterval: 30_000,
  });

  const brokers = [
    {
      name: "Zerodha",
      id: "zerodha",
      status: "phase4",
      description: "KiteConnect API integration",
      logo: "Z",
    },
    {
      name: "Upstox",
      id: "upstox",
      status: "phase4",
      description: "Upstox Order API v2",
      logo: "U",
    },
    {
      name: "Angel One",
      id: "angel",
      status: "future",
      description: "SmartAPI integration",
      logo: "A",
    },
    {
      name: "Dhan",
      id: "dhan",
      status: "future",
      description: "Dhan API integration",
      logo: "D",
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <SectionHeader
        title="Brokers"
        subtitle="Connect live broker accounts for real trade execution"
        action={<Badge variant="warning" size="md">Phase 4</Badge>}
      />

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wifi size={16} className="text-teal-400" />
            System Status
          </CardTitle>
        </CardHeader>
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "MongoDB", key: "mongodb" },
            { label: "Telegram", key: "telegram" },
          ].map(({ label, key }) => {
            const svc = health?.services?.[key as keyof typeof health.services];
            const ok = svc?.status === "ok";
            return (
              <div key={key} className="flex items-center gap-3 p-3 rounded-lg bg-slate-800/40">
                {ok
                  ? <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
                  : <XCircle size={16} className="text-red-400 shrink-0" />}
                <div>
                  <p className="text-sm font-medium text-white">{label}</p>
                  <p className={`text-xs ${ok ? "text-emerald-500" : "text-red-500"}`}>
                    {svc?.status ?? "checking..."}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Broker Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {brokers.map(broker => (
          <Card key={broker.id} className="border-dashed">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center font-bold text-xl text-slate-300">
                {broker.logo}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-semibold text-white">{broker.name}</p>
                  <Badge variant={broker.status === "phase4" ? "warning" : "muted"} size="sm">
                    {broker.status === "phase4" ? "Phase 4" : "Future"}
                  </Badge>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">{broker.description}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

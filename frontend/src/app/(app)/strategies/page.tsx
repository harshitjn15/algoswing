"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { SectionHeader, Card, CardHeader, CardTitle, Badge } from "@/components/ui";
import { Zap, Settings, CheckCircle2 } from "lucide-react";

export default function StrategiesPage() {
  const { data: strategies } = useQuery({
    queryKey: ["strategies"],
    queryFn: api.scanner.strategies,
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <SectionHeader
        title="Strategies"
        subtitle="Plugin-based trading strategy management"
      />

      <div className="space-y-4">
        {strategies?.map(strategy => (
          <Card key={strategy.id} className="border-teal-500/20">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center">
                  <Zap size={18} className="text-teal-400" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-white capitalize">
                      {strategy.name.replace(/_/g, " ")}
                    </p>
                    <Badge variant="default" size="sm">v{strategy.version}</Badge>
                    <Badge variant="profit" size="sm">
                      <CheckCircle2 size={10} className="mr-1" />
                      Active
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{strategy.description}</p>
                </div>
              </div>
              <button className="p-2 rounded-lg hover:bg-slate-800 text-slate-500 hover:text-slate-300 transition-colors">
                <Settings size={16} />
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 pt-4 border-t border-slate-800/40">
              {[
                { label: "ATH Range", value: "±5%" },
                { label: "Min Volume", value: "1.5x" },
                { label: "Max SL", value: "15%" },
                { label: "Targets", value: "10/15/20%" },
              ].map(({ label, value }) => (
                <div key={label} className="text-center p-2 bg-slate-800/30 rounded-lg">
                  <p className="text-[10px] text-slate-500 mb-1">{label}</p>
                  <p className="text-sm font-bold text-teal-400 font-mono">{value}</p>
                </div>
              ))}
            </div>
          </Card>
        ))}

        {/* Future strategies */}
        {["ATH Breakout", "Darvas Box", "Cup & Handle", "Volume Breakout"].map(name => (
          <Card key={name} className="border-dashed opacity-50">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center">
                <Zap size={18} className="text-slate-600" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-semibold text-slate-400">{name}</p>
                  <Badge variant="muted" size="sm">Phase 5</Badge>
                </div>
                <p className="text-xs text-slate-600">Coming in Phase 5</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

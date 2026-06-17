"use client";

import { Card, CardHeader, CardTitle, SectionHeader, Button } from "@/components/ui";
import { Settings, Bell, Shield, Palette, Database } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <SectionHeader title="Settings" subtitle="Configure your AlgoSwing platform" />

      {/* Risk Management */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield size={16} className="text-teal-400" />
            Risk Management
          </CardTitle>
        </CardHeader>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { label: "Capital (₹)", value: "100000", type: "number" },
            { label: "Risk Per Trade (%)", value: "2", type: "number" },
            { label: "Max Stop Loss (%)", value: "15", type: "number" },
            { label: "Max Open Positions", value: "5", type: "number" },
          ].map(({ label, value, type }) => (
            <div key={label}>
              <label className="text-xs text-slate-500 mb-1.5 block">{label}</label>
              <input
                type={type}
                defaultValue={value}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-teal-500/50"
              />
            </div>
          ))}
        </div>
        <div className="mt-4">
          <Button variant="primary" size="sm">Save Changes</Button>
        </div>
      </Card>

      {/* Alerts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell size={16} className="text-teal-400" />
            Alert Settings
          </CardTitle>
        </CardHeader>
        <div className="space-y-3">
          {[
            { label: "Telegram Alerts", desc: "Signal alerts via Telegram Bot" },
            { label: "Email Alerts",    desc: "Signal alerts via email" },
            { label: "SL Hit Alerts",   desc: "Notify when stop loss is triggered" },
            { label: "TP Hit Alerts",   desc: "Notify when targets are reached" },
          ].map(({ label, desc }) => (
            <div key={label} className="flex items-center justify-between py-2 border-b border-slate-800/40 last:border-0">
              <div>
                <p className="text-sm font-medium text-white">{label}</p>
                <p className="text-xs text-slate-500">{desc}</p>
              </div>
              <button className="w-10 h-5 bg-teal-500 rounded-full relative cursor-pointer">
                <span className="absolute right-0.5 top-0.5 w-4 h-4 bg-white rounded-full shadow" />
              </button>
            </div>
          ))}
        </div>
      </Card>

      {/* Connection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database size={16} className="text-teal-400" />
            API Connections
          </CardTitle>
        </CardHeader>
        <div className="space-y-3">
          {[
            { label: "Backend API URL", value: "http://localhost:8000" },
            { label: "Telegram Bot Token", value: "••••••••••••••••" },
            { label: "Telegram Chat ID", value: "••••••••" },
          ].map(({ label, value }) => (
            <div key={label}>
              <label className="text-xs text-slate-500 mb-1.5 block">{label}</label>
              <input
                type="text"
                defaultValue={value}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-300 focus:outline-none focus:border-teal-500/50 font-mono"
              />
            </div>
          ))}
        </div>
        <div className="mt-4">
          <Button variant="primary" size="sm">Save Connections</Button>
        </div>
      </Card>
    </div>
  );
}

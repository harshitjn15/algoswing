import React from "react";

export default function TerminalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col h-screen w-screen bg-gray-950 text-gray-200 overflow-hidden">
      
      {/* Top Panel: Watchlist & Signal Details */}
      <div className="flex h-1/4 border-b border-gray-800">
        <div className="w-1/4 border-r border-gray-800 p-2 overflow-y-auto">
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Watchlist</h2>
          <div className="text-sm text-gray-400 italic">Watchlist component placeholder...</div>
        </div>
        <div className="w-3/4 p-2 overflow-y-auto">
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Signal Details</h2>
          <div className="text-sm text-gray-400 italic">Strategy execution details placeholder...</div>
        </div>
      </div>

      {/* Main Panel: Charting Engine */}
      <div className="flex-1 relative">
        {children}
      </div>

      {/* Bottom Panel: Workstation Tools */}
      <div className="h-1/5 border-t border-gray-800 p-2 overflow-y-auto bg-gray-900">
        <div className="flex gap-4 border-b border-gray-800 pb-2 mb-2">
          <button className="text-xs font-bold text-blue-400 uppercase tracking-widest">Orders</button>
          <button className="text-xs font-bold text-gray-500 hover:text-gray-300 uppercase tracking-widest transition-colors">Trades</button>
          <button className="text-xs font-bold text-gray-500 hover:text-gray-300 uppercase tracking-widest transition-colors">Backtests</button>
          <button className="text-xs font-bold text-gray-500 hover:text-gray-300 uppercase tracking-widest transition-colors">Notes</button>
          <button className="text-xs font-bold text-gray-500 hover:text-gray-300 uppercase tracking-widest transition-colors">Alerts</button>
        </div>
        <div className="text-sm text-gray-400 italic">Order management placeholder...</div>
      </div>

    </div>
  );
}

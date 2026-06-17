"use client";

import React, { useState } from "react";
import { useChartStore } from "../stores/chart.store";
import { SearchSymbolResultItem } from "../types/tradingview";
import { ChartService } from "../services/chart.service";
import { Search, Maximize, Minimize, Moon, Sun } from "lucide-react";

const TIMEFRAMES = ["5M", "15M", "1H", "4H", "1D", "1W", "1M"];
const INTERVAL_MAP: Record<string, string> = {
  "5M": "5",
  "15M": "15",
  "1H": "60",
  "4H": "240",
  "1D": "1D",
  "1W": "1W",
  "1M": "1M",
};

export const ChartToolbar: React.FC = () => {
  const {
    selectedSymbol,
    selectedInterval,
    selectedTheme,
    isFullscreen,
    setSymbol,
    setInterval,
    setTheme,
    toggleFullscreen,
  } = useChartStore();

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchSymbolResultItem[]>([]);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (query.length > 1) {
      const results = await ChartService.searchSymbols(query);
      setSearchResults(results);
      setIsSearchOpen(true);
    } else {
      setSearchResults([]);
      setIsSearchOpen(false);
    }
  };

  const selectSymbol = (symbol: string) => {
    setSymbol(symbol);
    setIsSearchOpen(false);
    setSearchQuery("");
  };

  return (
    <div className="flex items-center justify-between p-2 bg-gray-900 border-b border-gray-800 text-sm h-14">
      {/* Symbol & Search */}
      <div className="flex items-center gap-4 relative">
        <div className="font-bold text-white px-3 py-1 bg-gray-800 rounded-md shadow-sm border border-gray-700 min-w-[120px] text-center">
          {selectedSymbol}
        </div>

        <div className="relative flex items-center bg-gray-800 border border-gray-700 rounded-md px-2 h-8 w-64">
          <Search size={14} className="text-gray-400 mr-2" />
          <input
            type="text"
            className="bg-transparent border-none outline-none text-white w-full text-sm placeholder-gray-500"
            placeholder="Search NSE symbols..."
            value={searchQuery}
            onChange={handleSearch}
            onFocus={() => { if (searchResults.length > 0) setIsSearchOpen(true) }}
            onBlur={() => setTimeout(() => setIsSearchOpen(false), 200)}
          />
          {isSearchOpen && searchResults.length > 0 && (
            <div className="absolute top-10 left-0 w-full bg-gray-800 border border-gray-700 rounded-md shadow-lg z-50 max-h-60 overflow-y-auto">
              {searchResults.map((res) => (
                <div
                  key={res.symbol}
                  className="px-3 py-2 hover:bg-gray-700 cursor-pointer text-white flex justify-between items-center"
                  onClick={() => selectSymbol(res.symbol)}
                >
                  <span className="font-semibold">{res.symbol}</span>
                  <span className="text-xs text-gray-400">{res.exchange}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Timeframes */}
      <div className="flex items-center gap-1 bg-gray-800 rounded-md p-1 border border-gray-700">
        {TIMEFRAMES.map((tf) => (
          <button
            key={tf}
            onClick={() => setInterval(INTERVAL_MAP[tf])}
            className={`px-3 py-1 rounded-sm transition-colors ${
              selectedInterval === INTERVAL_MAP[tf]
                ? "bg-blue-600 text-white font-medium shadow-sm"
                : "text-gray-400 hover:text-white hover:bg-gray-700"
            }`}
          >
            {tf}
          </button>
        ))}
      </div>

      {/* Tools & Settings */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setTheme(selectedTheme === "dark" ? "light" : "dark")}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-md transition-colors"
          title="Toggle Theme"
        >
          {selectedTheme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        <button
          onClick={toggleFullscreen}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-md transition-colors"
          title="Toggle Fullscreen"
        >
          {isFullscreen ? <Minimize size={16} /> : <Maximize size={16} />}
        </button>
      </div>
    </div>
  );
};

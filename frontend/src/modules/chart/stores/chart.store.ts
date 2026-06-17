import { create } from "zustand";

interface ChartState {
  selectedSymbol: string;
  selectedInterval: string;
  selectedTheme: "light" | "dark";
  isFullscreen: boolean;
  
  // Replay Mode Placeholders
  replayEnabled: boolean;
  replaySpeed: number;
  replayCursor: number | null;
  
  // Actions
  setSymbol: (symbol: string) => void;
  setInterval: (interval: string) => void;
  setTheme: (theme: "light" | "dark") => void;
  toggleFullscreen: () => void;
  
  // Replay Mode Actions
  setReplayEnabled: (enabled: boolean) => void;
  setReplaySpeed: (speed: number) => void;
  setReplayCursor: (cursor: number | null) => void;
}

export const useChartStore = create<ChartState>((set) => ({
  selectedSymbol: "NSE:RELIANCE",
  selectedInterval: "1D",
  selectedTheme: "dark",
  isFullscreen: false,
  
  replayEnabled: false,
  replaySpeed: 1,
  replayCursor: null,

  setSymbol: (symbol) => set({ selectedSymbol: symbol }),
  setInterval: (interval) => set({ selectedInterval: interval }),
  setTheme: (theme) => set({ selectedTheme: theme }),
  toggleFullscreen: () => set((state) => ({ isFullscreen: !state.isFullscreen })),
  
  setReplayEnabled: (enabled) => set({ replayEnabled: enabled }),
  setReplaySpeed: (speed) => set({ replaySpeed: speed }),
  setReplayCursor: (cursor) => set({ replayCursor: cursor }),
}));

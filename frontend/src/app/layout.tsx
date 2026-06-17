import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "AlgoSwing — Algorithmic Swing Trading",
    template: "%s | AlgoSwing",
  },
  description:
    "Production-grade algorithmic swing trading platform. IPO ATH Retest strategy with automated signals, paper trading, and broker integration.",
  keywords: ["algorithmic trading", "swing trading", "IPO ATH", "Zerodha", "Upstox", "NSE"],
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "AlgoSwing",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#0d9488",
};

import Script from "next/script";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning data-scroll-behavior="smooth">
      <head>
        <link rel="icon" href="data:," />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased">
        <Script 
          src="/charting_library/charting_library.standalone.js" 
          strategy="beforeInteractive" 
        />
        {children}
      </body>
    </html>
  );
}

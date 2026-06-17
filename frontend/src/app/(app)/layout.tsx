import { Providers } from "@/components/providers";
import { Sidebar, MobileNav, MobileHeader } from "@/components/layout/sidebar";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AlgoSwing — Trading Platform",
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <Providers>
      <div className="min-h-screen bg-[hsl(222,47%,5%)]">
        {/* Desktop sidebar */}
        <Sidebar />

        {/* Mobile header */}
        <MobileHeader />

        {/* Main content */}
        <main className="lg:ml-60 min-h-screen pb-20 lg:pb-0">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </div>
        </main>

        {/* Mobile bottom nav */}
        <MobileNav />
      </div>
    </Providers>
  );
}

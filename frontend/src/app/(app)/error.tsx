"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button, Card } from "@/components/ui";

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Dashboard Error Boundary Caught:", error);
  }, [error]);

  return (
    <div className="flex h-[80vh] w-full items-center justify-center p-4">
      <Card className="max-w-md p-8 text-center border-red-500/20 bg-red-500/5 shadow-2xl shadow-red-500/5">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-500/10">
          <AlertTriangle className="h-8 w-8 text-red-400" />
        </div>
        <h2 className="mb-2 text-xl font-bold text-white">Something went wrong</h2>
        <p className="mb-6 text-sm text-slate-400">
          We encountered an unexpected error while rendering this page.
          <br />
          <span className="font-mono text-xs text-red-300 mt-2 block p-2 bg-black/20 rounded">
            {error.message || "Unknown rendering error"}
          </span>
        </p>
        <Button
          variant="primary"
          onClick={() => reset()}
          icon={<RefreshCw size={14} />}
          className="w-full justify-center"
        >
          Try Again
        </Button>
      </Card>
    </div>
  );
}

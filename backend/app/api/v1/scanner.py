"""
AlgoSwing — Scanner API Router
POST /api/v1/scanner/run — trigger manual scan
GET  /api/v1/scanner/status — scheduler status
GET  /api/v1/scanner/strategies — list registered strategies
"""
import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger

from app.core.scheduler import is_market_open, run_scanner_job, get_scheduler
from app.strategies.registry import list_strategies

router = APIRouter(prefix="/scanner", tags=["scanner"])


@router.post("/run")
async def trigger_scan(background_tasks: BackgroundTasks):
    """
    Manually trigger a scan run.
    Runs in background — returns immediately.
    """
    logger.info("🔧 Manual scan triggered via API")
    background_tasks.add_task(run_scanner_job, force=True)
    return {
        "message": "Scan triggered",
        "market_open": is_market_open(),
        "note": "Results will appear in /signals and /watchlist",
    }


@router.post("/run-sync")
async def trigger_scan_sync():
    """
    Synchronously trigger a scan (waits for completion).
    Use for testing only — may time out in production.
    """
    logger.info("🔧 Synchronous scan triggered via API")
    try:
        await run_scanner_job(force=True)
        return {"message": "Scan completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("/status")
async def get_scanner_status():
    """Return scheduler status and next run time."""
    scheduler = get_scheduler()
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
        })

    return {
        "running": scheduler.running,
        "market_open": is_market_open(),
        "jobs": jobs,
    }


@router.get("/strategies")
async def get_strategies():
    """Return list of all registered trading strategies."""
    return list_strategies()

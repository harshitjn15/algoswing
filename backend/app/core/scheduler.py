"""
AlgoSwing Backend — APScheduler Configuration
Runs scanner and strategy jobs during market hours (IST).
"""
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

IST = pytz.timezone("Asia/Kolkata")
_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone=IST)
    return _scheduler


def is_market_open() -> bool:
    """Check if NSE market is currently open (Mon-Fri, 09:15-15:30 IST)."""
    now = datetime.now(IST)
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False

    open_h, open_m = map(int, settings.market_open_time.split(":"))
    close_h, close_m = map(int, settings.market_close_time.split(":"))

    market_open = now.replace(hour=open_h, minute=open_m, second=0, microsecond=0)
    market_close = now.replace(hour=close_h, minute=close_m, second=0, microsecond=0)

    return market_open <= now <= market_close


async def run_scanner_job(force: bool = False) -> None:
    """Wrapper that guards scanner execution to market hours only."""
    if not is_market_open() and not force:
        logger.debug("⏸  Market closed — skipping scanner run")
        return

    logger.info("🔍 Running scheduled scanner job...")

    # Import here to avoid circular imports
    from app.scanners.ipo_base import IPOBaseScanner
    from app.strategies.registry import get_strategy
    from app.strategies.ipo_ath_retest.strategy import IPOATHRetestStrategy
    from app.repositories.signals import SignalsRepository
    from app.repositories.watchlist import WatchlistRepository
    from app.repositories.trades import TradesRepository
    from app.services.risk_engine import RiskEngine
    from app.models.trade import Trade
    from app.alerts.telegram import TelegramAlert

    try:
        # 1. Run scanner
        scanner = IPOBaseScanner()
        stocks = await scanner.scan()
        logger.info(f"📋 Scanner returned {len(stocks)} stocks")

        # 2. Save to watchlist
        watchlist_repo = WatchlistRepository()
        await watchlist_repo.upsert_many(stocks)

        # 3. Run strategy on each stock
        strategy = IPOATHRetestStrategy()
        signals_repo = SignalsRepository()
        trades_repo = TradesRepository()
        risk_engine = RiskEngine()
        telegram = TelegramAlert()

        for stock in stocks:
            signal = await strategy.generate_signal(stock)
            if signal:
                logger.info(f"🚀 Signal generated: {signal.symbol} @ ₹{signal.entry:.2f}")
                saved = await signals_repo.create(signal)
                await telegram.send_signal(signal)
                
                # Auto Trade Execution
                if settings.auto_trade:
                    if await risk_engine.evaluate_signal(signal):
                        logger.info(f"🤖 Auto-Trading enabled: Entering paper trade for {signal.symbol}")
                        trade = Trade(
                            signal_id=saved._id,
                            user_id="bot",
                            symbol=signal.symbol,
                            strategy_id=signal.strategy_id,
                            entry_price=signal.entry,
                            qty=10,  # Fixed size for now
                            position_value=signal.entry * 10,
                            stop_loss=signal.stop_loss,
                            targets=signal.targets,
                            risk_amount=(signal.entry - signal.stop_loss) * 10,
                            risk_pct=signal.risk_pct,
                            current_price=signal.entry
                        )
                        await trades_repo.create(trade)

    except Exception as e:
        logger.error(f"❌ Scanner job failed: {e}", exc_info=True)


def setup_scheduler() -> AsyncIOScheduler:
    """Register all scheduled jobs and return configured scheduler."""
    scheduler = get_scheduler()

    # Scanner job — morning and night
    scheduler.add_job(
        run_scanner_job,
        trigger=CronTrigger(
            hour="9,21", minute="15", timezone=IST
        ),
        kwargs={"force": True},
        id="ipo_scanner",
        name="IPO Base Scan + ATH Retest Strategy",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping runs
    )

    # Daily pre-market warm-up (9:00 AM IST)
    scheduler.add_job(
        _premarket_warmup,
        trigger=CronTrigger(hour=9, minute=0, timezone=IST, day_of_week="mon-fri"),
        id="premarket_warmup",
        name="Pre-market data warm-up",
        replace_existing=True,
    )

    # Trade Manager job — every 5 minutes during market hours
    scheduler.add_job(
        run_trade_manager_job,
        trigger=IntervalTrigger(
            minutes=5,
            timezone=IST,
        ),
        id="trade_manager",
        name="Manage Active Paper Trades",
        replace_existing=True,
        max_instances=1,
    )

    logger.info("✅ Scheduler configured with all jobs")
    return scheduler

async def run_trade_manager_job() -> None:
    """Wrapper that guards trade manager execution to market hours only."""
    if not is_market_open():
        return

    from app.services.trade_manager import TradeManager
    try:
        manager = TradeManager()
        await manager.manage_active_trades()
    except Exception as e:
        logger.error(f"❌ Trade manager job failed: {e}", exc_info=True)

async def _premarket_warmup() -> None:
    """Pre-market: log startup, future: warm caches."""
    logger.info("🌅 Pre-market warm-up started")

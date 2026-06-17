"""
AlgoSwing — IPO ATH Retest Strategy
Full strategy implementation with all 5 rules.
Registered in the strategy plugin registry via @register_strategy.
"""
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger

from app.strategies.base import BaseStrategy
from app.strategies.registry import register_strategy
from app.strategies.ipo_ath_retest.filters import IPOATHFilters
from app.market_data.upstox import get_upstox_provider
from app.market_data.base import Candle
from app.models.signal import Signal, ConfidenceLevel
from app.models.watchlist import WatchlistEntry
from app.core.config import get_settings

settings = get_settings()


@register_strategy
class IPOATHRetestStrategy(BaseStrategy):
    """
    IPO ATH Retest Strategy

    Logic Flow:
    1. Stock in IPO Base Scan (near ATH)
    2. Rule 1: Near ATH ±5%
    3. Rule 2: Volume >= 1.5x 20-day avg
    4. Rule 3: ATH breakout detected in history
    5. Rule 4: Retest of breakout zone detected (volume contraction + held support)
    6. Rule 5: Entry trigger — bullish candle with volume expansion
    7. SL = nearest swing low (max 15%)
    8. TP1=10%, TP2=15%, TP3=20%
    """

    name = "ipo_ath_retest"
    version = "1.0.0"
    description = "IPO stocks that broke ATH and are retesting the breakout zone with volume confirmation"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._upstox = get_upstox_provider()
        self._filters = IPOATHFilters(
            ath_range_pct=self._get_config("ath_range_pct", settings.default_ath_range_pct),
            volume_multiplier=self._get_config("volume_multiplier", settings.default_volume_multiplier),
            retest_zone_low_pct=self._get_config("retest_zone_low_pct", settings.default_retest_zone_low_pct),
            retest_zone_high_pct=self._get_config("retest_zone_high_pct", settings.default_retest_zone_high_pct),
        )
        self._max_sl_pct = self._get_config("max_sl_pct", settings.default_max_sl_pct)

    async def scan(self, stocks: list[WatchlistEntry]) -> list[WatchlistEntry]:
        """
        Pre-filter: return only stocks that pass Rule 1 (near ATH).
        Full signal generation happens in generate_signal().
        """
        qualified = []
        for stock in stocks:
            if stock.ath and stock.last_close:
                if self._filters.rule1_near_ath(stock.last_close, stock.ath):
                    qualified.append(stock)

        logger.info(
            f"📋 {self.name} scan: {len(qualified)}/{len(stocks)} stocks near ATH"
        )
        return qualified

    async def generate_signal(self, stock: WatchlistEntry) -> Optional[Signal]:
        """
        Full 5-rule analysis for a single stock.
        Returns Signal if all conditions met, else None.
        """
        symbol = stock.symbol
        logger.info(f"🔍 Analyzing {symbol} for {self.name} signal...")

        # ── Rule 1: Near ATH ────────────────────────────
        if not stock.ath or not stock.last_close:
            logger.debug(f"{symbol}: Missing ATH or close data")
            return None

        if not self._filters.rule1_near_ath(stock.last_close, stock.ath):
            logger.debug(f"{symbol}: Rule 1 FAILED — not near ATH")
            return None

        # ── Fetch full candle history ────────────────────
        if not stock.isin or not stock.listing_date:
            logger.debug(f"{symbol}: Missing ISIN or listing date")
            return None

        instrument_key = f"NSE_EQ|{stock.isin}"
        today = datetime.utcnow().strftime("%Y-%m-%d")

        candles = await self._upstox.get_historical_candles(
            instrument_key=instrument_key,
            from_date=stock.listing_date,
            to_date=today,
        )

        if not candles or len(candles) < 10:
            logger.debug(f"{symbol}: Insufficient candle data ({len(candles)} candles)")
            return None

        # ── Rule 2: Volume Confirmation ───────────────────
        latest_volume = candles[0].volume
        avg_vol_20d = self._upstox.calculate_avg_volume(candles, days=20)

        if not self._filters.rule2_volume_confirmation(latest_volume, avg_vol_20d):
            logger.debug(f"{symbol}: Rule 2 FAILED — insufficient volume")
            return None

        # ── Rule 3: ATH Breakout ──────────────────────────
        breakout = self._filters.rule3_ath_breakout(candles)
        if not breakout:
            logger.debug(f"{symbol}: Rule 3 FAILED — no ATH breakout found")
            return None

        # ── Rule 4: Retest Detection ──────────────────────
        retest = self._filters.rule4_retest_detection(candles, breakout)
        if not retest:
            logger.debug(f"{symbol}: Rule 4 FAILED — no valid retest found")
            return None

        # ── Rule 5: Entry Trigger ──────────────────────────
        trigger = self._filters.rule5_entry_trigger(candles, retest)
        if not trigger:
            logger.debug(f"{symbol}: Rule 5 FAILED — no entry trigger")
            return None

        # ── Stop Loss Calculation ─────────────────────────
        entry = trigger.entry_price
        stop_loss = self.calculate_stoploss(symbol, entry, candles)
        risk_pct = self.calculate_risk_pct(entry, stop_loss)

        if not self.validate_stoploss(risk_pct, self._max_sl_pct):
            logger.warning(
                f"{symbol}: SL too wide — risk={risk_pct:.1f}% > max={self._max_sl_pct}%"
            )
            return None

        # ── Profit Targets ────────────────────────────────
        targets = self.calculate_targets(entry, stop_loss)
        rr_ratio = self.calculate_rr_ratio(entry, stop_loss, targets)

        # ── Confidence Score ──────────────────────────────
        confidence = self._calculate_confidence(
            volume_ratio=stock.volume_ratio or 0,
            ath_distance_pct=abs(stock.ath_distance_pct or 0),
            rr_ratio=rr_ratio,
        )

        signal = Signal(
            symbol=symbol,
            exchange="NSE",
            strategy_id=self.name,
            isin=stock.isin,
            entry=round(entry, 2),
            stop_loss=round(stop_loss, 2),
            targets=[round(t, 2) for t in targets],
            risk_pct=risk_pct,
            reward_risk_ratio=rr_ratio,
            ath=stock.ath,
            ath_date=stock.ath_date,
            ath_distance_pct=stock.ath_distance_pct or 0,
            breakout_date=breakout.breakout_date,
            breakout_price=breakout.breakout_price,
            breakout_volume=breakout.breakout_volume,
            volume_ratio=stock.volume_ratio or 0,
            avg_volume_20d=avg_vol_20d,
            confidence=confidence,
            notes=(
                f"Breakout: {breakout.breakout_date} @ ₹{breakout.breakout_price:.2f}. "
                f"Retest low: ₹{retest.retest_low:.2f}. "
                f"Trigger: {trigger.trigger_type}"
            ),
        )

        logger.info(
            f"🚀 Signal GENERATED: {symbol} | Entry: ₹{entry:.2f} | "
            f"SL: ₹{stop_loss:.2f} ({risk_pct:.1f}%) | "
            f"TP: {[round(t, 2) for t in targets]} | Confidence: {confidence}"
        )

        return signal

    def calculate_stoploss(
        self, symbol: str, entry: float, candles: list[Candle]
    ) -> float:
        """
        Stop loss = nearest swing low below entry.
        Looks back 10 candles for a swing low (local minimum).
        Falls back to percentage-based SL if no swing low found.
        """
        lookback = candles[:10]  # Most recent 10 candles (newest-first)
        lows = [c.low for c in lookback if c.low < entry]

        if lows:
            swing_low = max(lows)  # Nearest low below entry
        else:
            # Fallback: 8% below entry
            swing_low = entry * 0.92

        return round(swing_low, 2)

    def calculate_targets(self, entry: float, stop_loss: float) -> list[float]:
        """
        TP1 = entry + 10%
        TP2 = entry + 15%
        TP3 = entry + 20%
        """
        tp1_pct = self._get_config("tp1_pct", settings.default_tp1_pct) / 100
        tp2_pct = self._get_config("tp2_pct", settings.default_tp2_pct) / 100
        tp3_pct = self._get_config("tp3_pct", settings.default_tp3_pct) / 100

        return [
            round(entry * (1 + tp1_pct), 2),
            round(entry * (1 + tp2_pct), 2),
            round(entry * (1 + tp3_pct), 2),
        ]

    def _calculate_confidence(
        self,
        volume_ratio: float,
        ath_distance_pct: float,
        rr_ratio: float,
    ) -> ConfidenceLevel:
        """
        Confidence scoring:
        HIGH:   volume_ratio >= 2x, ATH dist <= 2%, RR >= 2
        MEDIUM: volume_ratio >= 1.5x, ATH dist <= 4%, RR >= 1.5
        LOW:    everything else
        """
        if volume_ratio >= 2.0 and ath_distance_pct <= 2.0 and rr_ratio >= 2.0:
            return ConfidenceLevel.HIGH
        elif volume_ratio >= 1.5 and ath_distance_pct <= 4.0 and rr_ratio >= 1.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def build_overlays(self, signal: Signal) -> list[dict]:
        """
        Constructs the overlays specifically for the IPO ATH strategy.
        Returns a list of dicts that the overlay_service will convert to OverlayData.
        """
        overlays = []
        
        # Entry Line
        overlays.append({
            "id": f"entry_{signal.id}",
            "type": "ENTRY",
            "price": signal.entry,
            "label": "Entry Trigger",
            "color": "#26a69a",
            "visible": True,
            "metadata": {"signal_id": str(signal.id)}
        })
        
        # Stop Loss Line
        overlays.append({
            "id": f"sl_{signal.id}",
            "type": "SL",
            "price": signal.stop_loss,
            "label": f"Stop Loss ({signal.risk_pct}%)",
            "color": "#ef5350",
            "visible": True,
            "metadata": {"signal_id": str(signal.id)}
        })
        
        # Breakout Zone Line
        if signal.breakout_price:
            overlays.append({
                "id": f"breakout_{signal.id}",
                "type": "BREAKOUT",
                "price": signal.breakout_price,
                "label": "Breakout Zone",
                "color": "#ff9800",
                "visible": True,
                "metadata": {"signal_id": str(signal.id)}
            })
            
        # Target Lines
        for i, tp in enumerate(signal.targets):
            overlays.append({
                "id": f"tp_{i+1}_{signal.id}",
                "type": "TARGET",
                "price": tp,
                "label": f"TP {i+1}",
                "color": "#4caf50",
                "visible": True,
                "metadata": {"signal_id": str(signal.id), "target_index": i}
            })
            
        return overlays

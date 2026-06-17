"""
AlgoSwing — IPO ATH Retest Strategy — Signal Filters
Implements the 5 screening rules from the product spec.

Rule 1: Near ATH (±5%)
Rule 2: Volume Confirmation (>= 1.5x 20-day avg)
Rule 3: ATH Breakout detection
Rule 4: Retest detection
Rule 5: Entry trigger (bullish confirmation + volume expansion)
"""
from dataclasses import dataclass
from typing import Optional

from loguru import logger

from app.market_data.base import Candle


@dataclass
class BreakoutInfo:
    """Stores details about an ATH breakout event."""
    breakout_date: str
    breakout_price: float
    breakout_volume: float
    pre_breakout_ath: float  # ATH before the breakout candle


@dataclass
class RetestInfo:
    """Stores details about a retest event after ATH breakout."""
    retest_start_date: str
    retest_low: float
    retest_low_date: str
    volume_contracted: bool  # Volume was lower during retest
    held_support: bool  # Price did not break below breakout zone


@dataclass
class EntryTrigger:
    """Final entry trigger confirmation."""
    entry_price: float
    trigger_date: str
    trigger_candle_volume: float
    trigger_type: str  # "BULLISH_CLOSE_ABOVE_RETEST"


class IPOATHFilters:
    """
    All 5 filtering rules for the IPO ATH Retest strategy.
    Each rule returns a bool (pass/fail) plus optional metadata.
    """

    def __init__(
        self,
        ath_range_pct: float = 5.0,
        volume_multiplier: float = 1.5,
        retest_zone_low_pct: float = 1.0,
        retest_zone_high_pct: float = 3.0,
    ):
        self.ath_range_pct = ath_range_pct
        self.volume_multiplier = volume_multiplier
        self.retest_zone_low_pct = retest_zone_low_pct
        self.retest_zone_high_pct = retest_zone_high_pct

    # ─── Rule 1: Near ATH ─────────────────────────────────
    def rule1_near_ath(self, last_close: float, ath: float) -> bool:
        """Stock must be within ±5% of All-Time High."""
        if ath <= 0:
            return False
        distance_pct = abs((last_close - ath) / ath) * 100
        result = distance_pct <= self.ath_range_pct
        logger.debug(
            f"Rule1 Near ATH: close={last_close:.2f}, ath={ath:.2f}, "
            f"dist={distance_pct:.2f}% → {'✅' if result else '❌'}"
        )
        return result

    # ─── Rule 2: Volume Confirmation ─────────────────────
    def rule2_volume_confirmation(
        self, current_volume: float, avg_volume_20d: float
    ) -> bool:
        """Current volume >= 1.5x 20-day average volume."""
        if avg_volume_20d <= 0:
            return False
        ratio = current_volume / avg_volume_20d
        result = ratio >= self.volume_multiplier
        logger.debug(
            f"Rule2 Volume: current={current_volume:.0f}, avg20d={avg_volume_20d:.0f}, "
            f"ratio={ratio:.2f}x → {'✅' if result else '❌'}"
        )
        return result

    # ─── Rule 3: ATH Breakout Detection ───────────────────
    def rule3_ath_breakout(
        self, candles: list[Candle]
    ) -> Optional[BreakoutInfo]:
        """
        Detect if a valid ATH breakout occurred in historical data.
        Valid breakout: close > previous rolling ATH.

        Looks for the MOST RECENT breakout event.
        Returns BreakoutInfo if found, else None.
        """
        if len(candles) < 5:
            return None

        # Candles are newest-first from Upstox — reverse for chronological scan
        chrono = list(reversed(candles))

        rolling_ath = chrono[0].high
        breakout_info: Optional[BreakoutInfo] = None

        for i in range(1, len(chrono)):
            c = chrono[i]
            prev_ath = rolling_ath

            if c.close > prev_ath:
                # ✅ Valid ATH breakout
                breakout_info = BreakoutInfo(
                    breakout_date=c.timestamp[:10],
                    breakout_price=c.close,
                    breakout_volume=c.volume,
                    pre_breakout_ath=prev_ath,
                )
                logger.debug(
                    f"Rule3 Breakout found: date={c.timestamp[:10]}, "
                    f"close={c.close:.2f} > prev_ath={prev_ath:.2f}"
                )

            rolling_ath = max(rolling_ath, c.high)

        if breakout_info:
            logger.debug(f"Rule3 ✅ Most recent breakout: {breakout_info}")
        else:
            logger.debug("Rule3 ❌ No ATH breakout found in history")

        return breakout_info

    # ─── Rule 4: Retest Detection ─────────────────────────
    def rule4_retest_detection(
        self,
        candles: list[Candle],
        breakout_info: BreakoutInfo,
    ) -> Optional[RetestInfo]:
        """
        After ATH breakout: detect if price retested the breakout zone.
        Retest = price pulls back to within 1-3% of breakout price,
        with contracting volume, and held support (no close below zone).
        """
        if not breakout_info:
            return None

        breakout_price = breakout_info.breakout_price
        zone_low = breakout_price * (1 - self.retest_zone_high_pct / 100)
        zone_high = breakout_price * (1 + self.retest_zone_low_pct / 100)

        # Get candles AFTER the breakout date (chronological order)
        chrono = list(reversed(candles))
        post_breakout = [
            c for c in chrono
            if c.timestamp[:10] > breakout_info.breakout_date
        ]

        if len(post_breakout) < 2:
            logger.debug("Rule4 ❌ Not enough post-breakout candles")
            return None

        # Calculate breakout day volume for comparison
        breakout_volume = breakout_info.breakout_volume

        retest_candles = []
        for c in post_breakout:
            if zone_low <= c.low <= zone_high or zone_low <= c.close <= zone_high:
                retest_candles.append(c)

        if not retest_candles:
            logger.debug(
                f"Rule4 ❌ No retest candle found in zone [{zone_low:.2f}, {zone_high:.2f}]"
            )
            return None

        # Check volume contraction during retest
        retest_volumes = [c.volume for c in retest_candles]
        avg_retest_volume = sum(retest_volumes) / len(retest_volumes)
        volume_contracted = avg_retest_volume < breakout_volume * 0.75

        # Check if price held support (no close below zone_low)
        closes_during_retest = [c.close for c in retest_candles]
        held_support = min(closes_during_retest) >= zone_low * 0.98  # 2% buffer

        retest_low = min(c.low for c in retest_candles)
        retest_low_date = min(retest_candles, key=lambda c: c.low).timestamp[:10]

        result = RetestInfo(
            retest_start_date=retest_candles[0].timestamp[:10],
            retest_low=retest_low,
            retest_low_date=retest_low_date,
            volume_contracted=volume_contracted,
            held_support=held_support,
        )

        logger.debug(
            f"Rule4 Retest: zone=[{zone_low:.2f},{zone_high:.2f}], "
            f"low={retest_low:.2f}, vol_contracted={volume_contracted}, "
            f"held_support={held_support}"
        )

        return result if (volume_contracted and held_support) else None

    # ─── Rule 5: Entry Trigger ────────────────────────────
    def rule5_entry_trigger(
        self,
        candles: list[Candle],
        retest_info: RetestInfo,
    ) -> Optional[EntryTrigger]:
        """
        Entry trigger: bullish confirmation candle after retest.
        - Volume expands (above 20-day avg)
        - Close above the retest high
        - Most recent candle = signal day

        Returns EntryTrigger if conditions met on the MOST RECENT candle.
        """
        if not retest_info or not candles:
            return None

        # Most recent candle (candles[0] = newest from Upstox)
        latest = candles[0]
        retest_high = retest_info.retest_low * 1.01  # 1% above retest low

        # Volume must expand vs average (simple threshold: > retest avg volume)
        avg_20d_vol = sum(c.volume for c in candles[:20]) / min(20, len(candles))
        volume_expands = latest.volume > avg_20d_vol

        # Bullish close: close must be above the retest high
        bullish_close = latest.close > retest_high

        # Candle must be AFTER retest
        after_retest = latest.timestamp[:10] >= retest_info.retest_start_date

        logger.debug(
            f"Rule5 Entry: close={latest.close:.2f}, retest_high={retest_high:.2f}, "
            f"vol_expands={volume_expands}, bullish_close={bullish_close}, "
            f"after_retest={after_retest}"
        )

        if volume_expands and bullish_close and after_retest:
            return EntryTrigger(
                entry_price=latest.close,
                trigger_date=latest.timestamp[:10],
                trigger_candle_volume=latest.volume,
                trigger_type="BULLISH_CLOSE_ABOVE_RETEST",
            )

        return None

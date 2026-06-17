"""
AlgoSwing — Unit Tests for IPO ATH Retest Strategy Filters
"""
import pytest
from app.strategies.ipo_ath_retest.filters import IPOATHFilters, BreakoutInfo, RetestInfo
from app.market_data.base import Candle


def make_candle(date: str, open_: float, high: float, low: float, close: float, vol: float) -> Candle:
    return Candle(timestamp=date, open=open_, high=high, low=low, close=close, volume=vol)


@pytest.fixture
def filters():
    return IPOATHFilters(
        ath_range_pct=5.0,
        volume_multiplier=1.5,
        retest_zone_low_pct=1.0,
        retest_zone_high_pct=3.0,
    )


# ─── Rule 1: Near ATH ─────────────────────────────────
class TestRule1NearATH:
    def test_within_range_passes(self, filters):
        assert filters.rule1_near_ath(last_close=1000.0, ath=1020.0) is True  # -1.96%

    def test_exactly_at_ath_passes(self, filters):
        assert filters.rule1_near_ath(last_close=1000.0, ath=1000.0) is True

    def test_above_ath_passes(self, filters):
        assert filters.rule1_near_ath(last_close=1040.0, ath=1000.0) is True  # +4%

    def test_too_far_below_fails(self, filters):
        assert filters.rule1_near_ath(last_close=900.0, ath=1000.0) is False  # -10%

    def test_exactly_at_boundary(self, filters):
        assert filters.rule1_near_ath(last_close=950.0, ath=1000.0) is True   # exactly -5%

    def test_zero_ath_fails(self, filters):
        assert filters.rule1_near_ath(last_close=1000.0, ath=0.0) is False


# ─── Rule 2: Volume Confirmation ─────────────────────
class TestRule2VolumeConfirmation:
    def test_above_threshold_passes(self, filters):
        assert filters.rule2_volume_confirmation(current_volume=200000, avg_volume_20d=100000) is True

    def test_exactly_at_threshold_passes(self, filters):
        assert filters.rule2_volume_confirmation(current_volume=150000, avg_volume_20d=100000) is True

    def test_below_threshold_fails(self, filters):
        assert filters.rule2_volume_confirmation(current_volume=100000, avg_volume_20d=100000) is False

    def test_zero_avg_fails(self, filters):
        assert filters.rule2_volume_confirmation(current_volume=100000, avg_volume_20d=0) is False


# ─── Rule 3: ATH Breakout ─────────────────────────────
class TestRule3ATHBreakout:
    def test_breakout_detected(self, filters):
        # Stock rallied from 100 to 150 (breakout at 150), then came back to 140
        candles = [
            make_candle("2024-01-10", 140, 145, 138, 140, 80000),   # newest (index 0)
            make_candle("2024-01-09", 148, 152, 146, 150, 250000),  # breakout day
            make_candle("2024-01-08", 130, 135, 128, 132, 60000),
            make_candle("2024-01-07", 120, 128, 118, 125, 50000),
            make_candle("2024-01-06", 110, 115, 108, 112, 45000),
        ]
        result = filters.rule3_ath_breakout(candles)
        assert result is not None
        assert result.breakout_price == 150

    def test_no_breakout_returns_none(self, filters):
        # Price always falling, never breaks ATH
        candles = [
            make_candle("2024-01-05", 100, 105, 98, 100, 50000),
            make_candle("2024-01-04", 110, 112, 108, 108, 48000),
            make_candle("2024-01-03", 115, 118, 113, 114, 45000),
            make_candle("2024-01-02", 120, 122, 118, 119, 42000),
            make_candle("2024-01-01", 125, 128, 124, 124, 40000),
        ]
        result = filters.rule3_ath_breakout(candles)
        assert result is None

    def test_too_few_candles_returns_none(self, filters):
        candles = [make_candle("2024-01-01", 100, 110, 98, 105, 50000)]
        result = filters.rule3_ath_breakout(candles)
        assert result is None


# ─── Rule 5: Entry Trigger ─────────────────────────────
class TestRule5EntryTrigger:
    def test_bullish_trigger_detected(self, filters):
        retest = RetestInfo(
            retest_start_date="2024-01-07",
            retest_low=145.0,
            retest_low_date="2024-01-08",
            volume_contracted=True,
            held_support=True,
        )
        # Newest candle should close above retest high (145 * 1.01 = 146.45) with high volume
        candles = [
            make_candle("2024-01-10", 147, 152, 146, 151, 300000),  # trigger candle
            make_candle("2024-01-09", 145, 148, 144, 146, 80000),
            make_candle("2024-01-08", 146, 148, 143, 145, 60000),  # retest low
            make_candle("2024-01-07", 149, 151, 145, 147, 70000),
            make_candle("2024-01-06", 150, 155, 148, 152, 200000),
            make_candle("2024-01-05", 148, 151, 147, 150, 190000),
        ] * 4  # Repeat to get >20 candles for volume avg

        result = filters.rule5_entry_trigger(candles, retest)
        assert result is not None
        assert result.entry_price == 151

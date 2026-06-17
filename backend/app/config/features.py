import os

class FeatureFlags:
    """
    Global toggles for major functionality.
    Sourced from environment variables in production.
    """
    ENABLE_PAPER_TRADING: bool = os.getenv("ENABLE_PAPER_TRADING", "true").lower() == "true"
    ENABLE_LIVE_TRADING: bool = os.getenv("ENABLE_LIVE_TRADING", "false").lower() == "true"
    ENABLE_BACKTESTING: bool = os.getenv("ENABLE_BACKTESTING", "true").lower() == "true"
    ENABLE_REPLAY: bool = os.getenv("ENABLE_REPLAY", "true").lower() == "true"

features = FeatureFlags()

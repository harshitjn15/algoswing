"""
AlgoSwing Backend — Application Settings
Loaded from environment variables via pydantic-settings
"""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ─────────────────────────────────
    app_env: str = "development"
    app_name: str = "AlgoSwing"
    app_version: str = "1.0.0"
    debug: bool = True
    port: int = 8000

    # ─── MongoDB ─────────────────────────────────────
    mongodb_url: str = Field(..., description="MongoDB Atlas connection string")
    mongodb_db_name: str = "algoswing"

    # ─── Upstox ──────────────────────────────────────
    upstox_access_token: str = ""
    upstox_api_key: str = ""
    upstox_api_secret: str = ""

    # ─── Zerodha ─────────────────────────────────────
    zerodha_api_key: str = ""
    zerodha_api_secret: str = ""
    zerodha_access_token: str = ""

    # ─── Telegram ────────────────────────────────────
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # ─── Email ───────────────────────────────────────
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_from_email: str = ""
    alert_to_email: str = ""

    # ─── CORS ────────────────────────────────────────
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    # ─── Scanner ─────────────────────────────────────
    scanner_interval_minutes: int = 30
    market_open_time: str = "09:15"
    market_close_time: str = "15:30"
    market_timezone: str = "Asia/Kolkata"
    auto_trade: bool = False

    # ─── Strategy Defaults ───────────────────────────
    default_ath_range_pct: float = 5.0
    default_volume_multiplier: float = 1.5
    default_max_sl_pct: float = 15.0
    default_tp1_pct: float = 10.0
    default_tp2_pct: float = 15.0
    default_tp3_pct: float = 20.0
    default_retest_zone_low_pct: float = 1.0
    default_retest_zone_high_pct: float = 3.0


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()

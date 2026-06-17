"""
AlgoSwing — Telegram Alert Service
Sends formatted trade signals via Telegram Bot API.
"""
import asyncio
from typing import Optional

import httpx
from loguru import logger

from app.core.config import get_settings
from app.models.signal import Signal, ConfidenceLevel

settings = get_settings()

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"

# Confidence emoji mapping
CONFIDENCE_EMOJI = {
    ConfidenceLevel.HIGH: "🔥",
    ConfidenceLevel.MEDIUM: "⚡",
    ConfidenceLevel.LOW: "📊",
}


class TelegramAlert:
    """
    Telegram Bot alert sender.
    Sends formatted signal messages to a configured chat.
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
    ):
        self._token = bot_token or settings.telegram_bot_token
        self._chat_id = chat_id or settings.telegram_chat_id
        self._api_url = TELEGRAM_API_URL.format(token=self._token)

    def _enabled(self) -> bool:
        """Check if Telegram is configured."""
        return bool(self._token and self._chat_id)

    def _format_signal_message(self, signal: Signal) -> str:
        """
        Format signal as the specified Telegram message template.

        🚀 IPO ATH RETEST SIGNAL
        Stock: XYZ
        Entry: ₹1250
        SL: ₹1140
        Risk: 8.8%
        TP1: ₹1375
        TP2: ₹1437
        TP3: ₹1500
        Strategy: IPO ATH Retest
        Confidence: High
        """
        conf_emoji = CONFIDENCE_EMOJI.get(signal.confidence, "📊")
        targets = signal.targets

        tp1 = f"₹{targets[0]:,.2f}" if len(targets) > 0 else "N/A"
        tp2 = f"₹{targets[1]:,.2f}" if len(targets) > 1 else "N/A"
        tp3 = f"₹{targets[2]:,.2f}" if len(targets) > 2 else "N/A"

        msg = (
            f"🚀 *IPO ATH RETEST SIGNAL*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Stock:* `{signal.symbol}`\n"
            f"💰 *Entry:* ₹{signal.entry:,.2f}\n"
            f"🛑 *SL:* ₹{signal.stop_loss:,.2f}\n"
            f"⚠️ *Risk:* {signal.risk_pct:.1f}%\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 *TP1:* {tp1} *(+{settings.default_tp1_pct:.0f}%)*\n"
            f"🎯 *TP2:* {tp2} *(+{settings.default_tp2_pct:.0f}%)*\n"
            f"🎯 *TP3:* {tp3} *(+{settings.default_tp3_pct:.0f}%)*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📈 *ATH:* ₹{signal.ath:,.2f}"
            f" ({signal.ath_distance_pct:+.1f}% from ATH)\n"
            f"📊 *Volume Ratio:* {signal.volume_ratio:.1f}x\n"
            f"🔢 *RR Ratio:* 1:{signal.reward_risk_ratio:.1f}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🧠 *Strategy:* IPO ATH Retest\n"
            f"{conf_emoji} *Confidence:* {signal.confidence.value}\n"
        )

        if signal.breakout_date:
            msg += f"📅 *Breakout:* {signal.breakout_date} @ ₹{signal.breakout_price:,.2f}\n"

        msg += f"\n_AlgoSwing • {signal.generated_at.strftime('%d %b %Y %H:%M')} IST_"

        return msg

    def _format_alert_message(self, title: str, body: str) -> str:
        """Format a generic alert message."""
        return f"*{title}*\n\n{body}"

    async def send_signal(self, signal: Signal) -> bool:
        """Send a trade signal alert to Telegram."""
        if not self._enabled():
            logger.warning("⚠️  Telegram not configured — skipping signal alert")
            return False

        message = self._format_signal_message(signal)
        return await self._send_message(message)

    async def send_text(self, title: str, body: str) -> bool:
        """Send a generic text message."""
        if not self._enabled():
            return False
        message = self._format_alert_message(title, body)
        return await self._send_message(message)

    async def send_error(self, error: str, context: str = "") -> bool:
        """Send an error notification."""
        if not self._enabled():
            return False
        msg = f"🚨 *AlgoSwing Error*\n\n`{error}`"
        if context:
            msg += f"\n\n_Context: {context}_"
        return await self._send_message(msg)

    async def _send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Send a raw message to Telegram API."""
        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self._api_url, json=payload)

            if resp.status_code == 200:
                logger.info(f"✅ Telegram message sent")
                return True
            else:
                logger.error(
                    f"❌ Telegram API error {resp.status_code}: {resp.text[:200]}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Telegram send failed: {e}")
            return False

    async def test_connection(self) -> dict:
        """Test bot connection via getMe endpoint."""
        test_url = f"https://api.telegram.org/bot{self._token}/getMe"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(test_url)
            data = resp.json()
            if data.get("ok"):
                bot = data.get("result", {})
                return {
                    "connected": True,
                    "bot_name": bot.get("first_name"),
                    "bot_username": bot.get("username"),
                }
            return {"connected": False, "error": data.get("description")}
        except Exception as e:
            return {"connected": False, "error": str(e)}

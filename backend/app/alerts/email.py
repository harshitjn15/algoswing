"""
AlgoSwing — Email Alert Service
Sends formatted trade signal emails via SMTP.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from loguru import logger

from app.core.config import get_settings
from app.models.signal import Signal

settings = get_settings()


class EmailAlert:
    """
    SMTP-based email alert sender.
    Sends HTML-formatted signal emails.
    """

    def __init__(self):
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._user = settings.smtp_user
        self._password = settings.smtp_password
        self._from_email = settings.alert_from_email
        self._to_email = settings.alert_to_email

    def _enabled(self) -> bool:
        return bool(self._user and self._password and self._to_email)

    def _build_signal_html(self, signal: Signal) -> str:
        """Build an HTML email body for a signal."""
        targets = signal.targets
        tp1 = f"₹{targets[0]:,.2f}" if len(targets) > 0 else "N/A"
        tp2 = f"₹{targets[1]:,.2f}" if len(targets) > 1 else "N/A"
        tp3 = f"₹{targets[2]:,.2f}" if len(targets) > 2 else "N/A"

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #1a1a2e; color: #eee; padding: 20px; border-radius: 12px;">
                <h2 style="color: #00d4aa; margin-top: 0;">🚀 IPO ATH Retest Signal</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #aaa;">Stock</td>
                        <td style="padding: 8px 0; font-weight: bold; color: #fff;">{signal.symbol}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #aaa;">Entry</td>
                        <td style="padding: 8px 0; color: #00d4aa;">₹{signal.entry:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #aaa;">Stop Loss</td>
                        <td style="padding: 8px 0; color: #ff4757;">₹{signal.stop_loss:,.2f} ({signal.risk_pct:.1f}%)</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #aaa;">TP1</td>
                        <td style="padding: 8px 0; color: #2ed573;">{tp1}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #aaa;">TP2</td>
                        <td style="padding: 8px 0; color: #2ed573;">{tp2}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #aaa;">TP3</td>
                        <td style="padding: 8px 0; color: #2ed573;">{tp3}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #aaa;">ATH</td>
                        <td style="padding: 8px 0; color: #fff;">₹{signal.ath:,.2f} ({signal.ath_distance_pct:+.1f}%)</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #aaa;">Volume Ratio</td>
                        <td style="padding: 8px 0; color: #fff;">{signal.volume_ratio:.1f}x</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #aaa;">Confidence</td>
                        <td style="padding: 8px 0; color: #ffd32a;">{signal.confidence.value}</td>
                    </tr>
                </table>
                <p style="margin-top: 20px; color: #666; font-size: 12px;">
                    AlgoSwing • {signal.generated_at.strftime('%d %b %Y %H:%M')} IST
                </p>
            </div>
        </body>
        </html>
        """

    def send_signal(self, signal: Signal) -> bool:
        """Send a signal alert email (synchronous SMTP)."""
        if not self._enabled():
            logger.warning("⚠️  Email not configured — skipping")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🚀 AlgoSwing Signal: {signal.symbol} | {signal.strategy.upper()}"
            msg["From"] = self._from_email
            msg["To"] = self._to_email

            html_content = self._build_signal_html(signal)
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(self._host, self._port) as server:
                server.starttls()
                server.login(self._user, self._password)
                server.sendmail(self._from_email, self._to_email, msg.as_string())

            logger.info(f"✅ Email alert sent for {signal.symbol}")
            return True

        except Exception as e:
            logger.error(f"❌ Email send failed: {e}")
            return False

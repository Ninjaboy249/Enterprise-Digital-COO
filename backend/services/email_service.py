"""
Demo approval email service.

Sends real email when SMTP settings are configured. Without SMTP, it returns a
demo capture response so the approval flow can still be shown safely.
"""
from __future__ import annotations

import asyncio
import re
import smtplib
from email.message import EmailMessage
from typing import Any, Dict, Optional

from config import settings


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class InvalidEmailError(ValueError):
    """Raised when a demo recipient email is invalid."""


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class EmailService:
    def __init__(self) -> None:
        self.smtp_host = _clean(settings.SMTP_HOST)
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = _clean(settings.SMTP_USERNAME)
        self.smtp_password = _clean(settings.SMTP_PASSWORD)
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.email_from = _clean(settings.EMAIL_FROM) or self.smtp_username

    @property
    def is_configured(self) -> bool:
        return bool(self.smtp_host and self.email_from)

    async def send_approval_email(
        self,
        recipient: str,
        *,
        action: str,
        signal: Optional[str] = None,
    ) -> Dict[str, Any]:
        email = recipient.strip()
        if not EMAIL_RE.match(email):
            raise InvalidEmailError("Enter a valid email address.")

        subject = "Enterprise Digital COO approval"
        body = (
            "Your Enterprise Digital COO action has been approved.\n\n"
            f"Signal: {signal or 'Executive action'}\n"
            f"Approved action: {action}\n\n"
            "This is a demo notification from Enterprise Digital COO."
        )

        if not self.is_configured:
            return {
                "ok": True,
                "mode": "demo_capture",
                "delivered": False,
                "recipient": email,
                "subject": subject,
                "preview": body,
            }

        await asyncio.to_thread(self._send_sync, email, subject, body)
        return {
            "ok": True,
            "mode": "smtp",
            "delivered": True,
            "recipient": email,
            "subject": subject,
        }

    def _send_sync(self, recipient: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self.email_from
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
            if self.smtp_use_tls:
                server.starttls()
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            server.send_message(message)


email_service = EmailService()

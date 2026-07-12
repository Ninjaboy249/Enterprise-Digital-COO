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
        executive_brief: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        email = recipient.strip()
        if not EMAIL_RE.match(email):
            raise InvalidEmailError("Enter a valid email address.")

        brief = executive_brief or {}
        subject = "Enterprise Digital COO"
        body = "\n".join(
            [
                "Dear Executive,",
                "",
                "The following Enterprise Digital COO recommendation has been approved.",
                "",
                "EXECUTIVE BRIEF",
                f"Fiscal Year: {brief.get('fiscal_year') or 'Not provided'}",
                f"AI Confidence: {brief.get('confidence') or 'Not provided'}",
                "",
                f"Signal: {brief.get('signal') or signal or 'Executive action'}",
                f"Business Context: {brief.get('cause') or 'Not provided'}",
                "",
                "PREDICTED FY IMPACT",
                f"Impact: {brief.get('predicted_impact') or 'Not provided'}",
                f"Impact Detail: {brief.get('impact_detail') or 'Not provided'}",
                f"AI Opportunity: {brief.get('ai_opportunity') or 'Not provided'}",
                f"Potential Savings: {brief.get('potential_savings') or 'Not provided'}",
                "",
                "KPI SNAPSHOT",
                f"Revenue: {brief.get('revenue') or 'Not provided'}",
                f"Cash: {brief.get('cash') or 'Not provided'}",
                f"CSAT: {brief.get('csat') or 'Not provided'}",
                f"Users: {brief.get('users') or 'Not provided'}",
                "",
                "RECOMMENDED ACTION",
                brief.get("recommended_action") or action,
                "",
                "Please review the approved action and proceed with the appropriate next steps.",
                "",
                "Regards,",
                "Enterprise Digital COO",
                "AI Command Center",
            ]
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

    async def send_generated_email(
        self,
        recipient: str,
        *,
        subject: str,
        body: str,
    ) -> Dict[str, Any]:
        email = recipient.strip()
        clean_subject = subject.strip()
        clean_body = body.strip()
        if not EMAIL_RE.match(email):
            raise InvalidEmailError("Enter a valid recipient email address.")
        if not clean_subject:
            raise ValueError("Email subject is required.")
        if not clean_body:
            raise ValueError("Email body is required.")
        if not self.is_configured:
            return {
                "ok": True,
                "mode": "demo_capture",
                "delivered": False,
                "recipient": email,
                "subject": clean_subject,
                "preview": clean_body,
            }
        await asyncio.to_thread(self._send_sync, email, clean_subject, clean_body)
        return {
            "ok": True,
            "mode": "smtp",
            "delivered": True,
            "recipient": email,
            "subject": clean_subject,
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

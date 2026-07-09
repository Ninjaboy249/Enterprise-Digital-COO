"""
Slack notification service.

Supports two simple outbound modes:
- Incoming webhook: easiest channel alert setup.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from config import settings


class SlackNotConfiguredError(RuntimeError):
    """Raised when Slack credentials are not available."""


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class SlackService:
    def __init__(self) -> None:
        self.webhook_url = _clean(settings.SLACK_WEBHOOK_URL)

    @property
    def is_configured(self) -> bool:
        return bool(self.webhook_url)

    async def send_message(
        self,
        text: str,
        *,
        channel: Optional[str] = None,
        blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not text.strip():
            raise ValueError("Slack message text cannot be empty.")

        if self.webhook_url:
            return await self._send_with_webhook(text, blocks)

        raise SlackNotConfiguredError("Slack is not configured. Set SLACK_WEBHOOK_URL.")

    async def _send_with_webhook(
        self,
        text: str,
        blocks: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"text": text}
        if blocks:
            payload["blocks"] = blocks

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.webhook_url, json=payload)

        if response.status_code >= 400:
            raise RuntimeError(
                f"Slack webhook failed with HTTP {response.status_code}: {response.text}"
            )
        if response.text.strip().lower() != "ok":
            raise RuntimeError(f"Slack webhook returned unexpected response: {response.text}")

        return {"ok": True, "mode": "webhook", "status_code": response.status_code}

slack_service = SlackService()

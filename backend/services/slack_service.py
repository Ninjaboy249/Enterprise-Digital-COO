"""
Slack notification service.

Supports two simple outbound modes:
- Incoming webhook: easiest channel alert setup.
- Bot token + channel: useful when callers need channel selection.
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
        self.bot_token = _clean(settings.SLACK_BOT_TOKEN)
        self.default_channel = _clean(settings.SLACK_DEFAULT_CHANNEL)

    @property
    def is_configured(self) -> bool:
        return bool(self.webhook_url or (self.bot_token and self.default_channel))

    async def send_message(
        self,
        text: str,
        *,
        channel: Optional[str] = None,
        blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not text.strip():
            raise ValueError("Slack message text cannot be empty.")

        target_channel = _clean(channel) or self.default_channel
        if self.bot_token and target_channel:
            return await self._send_with_bot_token(text, target_channel, blocks)
        if self.webhook_url:
            return await self._send_with_webhook(text, blocks)

        raise SlackNotConfiguredError(
            "Slack is not configured. Set SLACK_WEBHOOK_URL, or set "
            "SLACK_BOT_TOKEN and SLACK_DEFAULT_CHANNEL."
        )

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

    async def _send_with_bot_token(
        self,
        text: str,
        channel: str,
        blocks: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"channel": channel, "text": text}
        if blocks:
            payload["blocks"] = blocks

        headers = {"Authorization": f"Bearer {self.bot_token}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://slack.com/api/chat.postMessage",
                headers=headers,
                json=payload,
            )

        try:
            body = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Slack API returned non-JSON response with HTTP {response.status_code}."
            ) from exc

        if response.status_code >= 400 or not body.get("ok"):
            error = body.get("error", response.text)
            raise RuntimeError(f"Slack API failed: {error}")

        return {
            "ok": True,
            "mode": "bot",
            "channel": body.get("channel"),
            "ts": body.get("ts"),
        }


slack_service = SlackService()

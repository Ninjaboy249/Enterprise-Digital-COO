"""
Microsoft Teams notification service.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from config import settings


class TeamsNotConfiguredError(RuntimeError):
    """Raised when Teams webhook credentials are not available."""


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class TeamsService:
    def __init__(self) -> None:
        self.webhook_url = _clean(settings.TEAMS_WEBHOOK_URL)

    @property
    def is_configured(self) -> bool:
        return bool(self.webhook_url)

    async def send_message(self, text: str, *, title: str = "Enterprise Digital COO") -> Dict[str, Any]:
        if not text.strip():
            raise ValueError("Teams message text cannot be empty.")
        if not self.webhook_url:
            raise TeamsNotConfiguredError("Teams is not configured. Set TEAMS_WEBHOOK_URL.")

        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": "2563EB",
            "summary": title,
            "title": title,
            "text": text.replace("\n", "<br>"),
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.webhook_url, json=payload)

        if response.status_code >= 400:
            raise RuntimeError(
                f"Teams webhook failed with HTTP {response.status_code}: {response.text}"
            )

        return {"ok": True, "mode": "teams_webhook", "status_code": response.status_code}


teams_service = TeamsService()

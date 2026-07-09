"""
Notification API endpoints.
"""
import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.email_service import InvalidEmailError, email_service
from services.slack_service import SlackNotConfiguredError, slack_service
from services.teams_service import TeamsNotConfiguredError, teams_service

router = APIRouter()


class SlackMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=3000)
    channel: Optional[str] = None
    blocks: Optional[List[Dict[str, Any]]] = None


class TeamsMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=3000)
    title: str = Field("Enterprise Digital COO", min_length=1, max_length=120)


class ApprovalNotificationRequest(BaseModel):
    action: str = Field(..., min_length=1, max_length=1000)
    signal: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = Field(None, max_length=320)
    send_slack: bool = False
    send_teams: bool = False
    send_email: bool = False
    channel: Optional[str] = None


def _slack_error(exc: Exception) -> HTTPException:
    if isinstance(exc, SlackNotConfiguredError):
        return HTTPException(status_code=503, detail=str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=502, detail=f"Slack notification failed: {exc}")


def _teams_error(exc: Exception) -> HTTPException:
    if isinstance(exc, TeamsNotConfiguredError):
        return HTTPException(status_code=503, detail=str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=502, detail=f"Teams notification failed: {exc}")


def _email_error(exc: Exception) -> HTTPException:
    if isinstance(exc, InvalidEmailError):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=502, detail=f"Approval email failed: {exc}")


def _current_fy() -> int:
    return datetime.now().year


def _coo_summary_metrics(fy: int) -> Dict[str, Any]:
    sales_base = 1_000_000 * (1 + (fy - 2022) * 0.12)
    sales_factor = 1 + math.sin(fy) * 0.05
    revenue = round(sales_base * sales_factor)
    expected_revenue = round(revenue / 0.85)
    cash_balance = round(12_000_000 + (fy - 2022) * 1_200_000)
    burn_rate = round(1_100_000 + (fy - 2022) * 50_000)

    return {
        "revenue": revenue,
        "revenue_gap_pct": round((expected_revenue - revenue) / expected_revenue * 100, 1),
        "cash_runway_months": round(cash_balance / burn_rate, 1),
        "customer_satisfaction": round(4.0 + (fy - 2022) * 0.08, 1),
        "nps_score": 42 + (fy - 2022) * 3,
    }


def _approval_text(action: str, signal: Optional[str]) -> str:
    return (
        "Enterprise Digital COO approval\n"
        f"Signal: {signal or 'Executive action'}\n"
        f"Approved action: {action}"
    )


@router.get("/integrations/status")
async def integrations_status() -> Dict[str, Any]:
    """Return all notification integration states without exposing secrets."""
    return {
        "slack": {
            "configured": slack_service.is_configured,
            "has_webhook": bool(slack_service.webhook_url),
            "has_bot_token": bool(slack_service.bot_token),
            "has_default_channel": bool(slack_service.default_channel),
        },
        "teams": {
            "configured": teams_service.is_configured,
            "has_webhook": bool(teams_service.webhook_url),
        },
        "email": {
            "configured": email_service.is_configured,
            "mode": "smtp" if email_service.is_configured else "demo_capture",
        },
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/slack/status")
async def slack_status() -> Dict[str, Any]:
    """Return Slack configuration status without exposing secrets."""
    return {
        "configured": slack_service.is_configured,
        "has_webhook": bool(slack_service.webhook_url),
        "has_bot_token": bool(slack_service.bot_token),
        "has_default_channel": bool(slack_service.default_channel),
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/slack/message")
async def send_slack_message(req: SlackMessageRequest) -> Dict[str, Any]:
    """Send a custom Slack message."""
    try:
        result = await slack_service.send_message(
            req.text,
            channel=req.channel,
            blocks=req.blocks,
        )
        return {"sent": True, **result, "timestamp": datetime.now().isoformat()}
    except Exception as exc:
        raise _slack_error(exc)


@router.post("/slack/test")
async def send_slack_test() -> Dict[str, Any]:
    """Send a small test notification to verify Slack configuration."""
    try:
        result = await slack_service.send_message(
            "Enterprise Digital COO Slack integration is connected."
        )
        return {"sent": True, **result, "timestamp": datetime.now().isoformat()}
    except Exception as exc:
        raise _slack_error(exc)


@router.get("/teams/status")
async def teams_status() -> Dict[str, Any]:
    """Return Teams configuration status without exposing secrets."""
    return {
        "configured": teams_service.is_configured,
        "has_webhook": bool(teams_service.webhook_url),
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/teams/message")
async def send_teams_message(req: TeamsMessageRequest) -> Dict[str, Any]:
    """Send a custom Microsoft Teams message."""
    try:
        result = await teams_service.send_message(req.text, title=req.title)
        return {"sent": True, **result, "timestamp": datetime.now().isoformat()}
    except Exception as exc:
        raise _teams_error(exc)


@router.post("/teams/test")
async def send_teams_test() -> Dict[str, Any]:
    """Send a small test notification to verify Teams configuration."""
    try:
        result = await teams_service.send_message(
            "Enterprise Digital COO Teams integration is connected."
        )
        return {"sent": True, **result, "timestamp": datetime.now().isoformat()}
    except Exception as exc:
        raise _teams_error(exc)


@router.post("/teams/coo-summary")
async def send_teams_coo_summary_alert() -> Dict[str, Any]:
    """Send the current COO health summary as a Teams alert."""
    fy = _current_fy()
    metrics = _coo_summary_metrics(fy)
    text = (
        f"FY {fy}<br>"
        f"Revenue: ${metrics['revenue']:,.0f} "
        f"({metrics['revenue_gap_pct']}% below expected)<br>"
        f"Cash runway: {metrics['cash_runway_months']} months<br>"
        f"CSAT: {metrics['customer_satisfaction']}/5.0 | "
        f"NPS: {metrics['nps_score']}<br><br>"
        "Recommended action: prioritize pipeline acceleration, customer save plan, "
        "inventory rebalance, and cash protection."
    )
    try:
        result = await teams_service.send_message(
            text,
            title=f"Enterprise Digital COO - FY {fy}",
        )
        return {"sent": True, **result, "timestamp": datetime.now().isoformat()}
    except Exception as exc:
        raise _teams_error(exc)


@router.get("/email/status")
async def email_status() -> Dict[str, Any]:
    """Return approval email configuration status without exposing secrets."""
    return {
        "configured": email_service.is_configured,
        "mode": "smtp" if email_service.is_configured else "demo_capture",
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/approval")
async def send_approval_notification(req: ApprovalNotificationRequest) -> Dict[str, Any]:
    """Send an approved-action notification to selected demo integrations."""
    results: Dict[str, Any] = {}
    text = _approval_text(req.action, req.signal)

    if req.send_slack:
        try:
            results["slack"] = await slack_service.send_message(text, channel=req.channel)
        except Exception as exc:
            results["slack"] = {"ok": False, "error": str(exc)}

    if req.send_teams:
        try:
            results["teams"] = await teams_service.send_message(
                text,
                title="Enterprise Digital COO approval",
            )
        except Exception as exc:
            results["teams"] = {"ok": False, "error": str(exc)}

    if req.send_email:
        if not req.email:
            raise HTTPException(status_code=400, detail="Email address is required.")
        try:
            results["email"] = await email_service.send_approval_email(
                req.email,
                action=req.action,
                signal=req.signal,
            )
        except Exception as exc:
            raise _email_error(exc)

    if not results:
        raise HTTPException(status_code=400, detail="Select at least one notification target.")

    return {
        "ok": True,
        "results": results,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/slack/coo-summary")
async def send_coo_summary_alert() -> Dict[str, Any]:
    """Send the current COO health summary as a Slack alert."""
    fy = _current_fy()
    metrics = _coo_summary_metrics(fy)

    text = (
        f"Enterprise Digital COO alert - FY {fy}\n"
        f"Revenue: ${metrics['revenue']:,.0f} "
        f"({metrics['revenue_gap_pct']}% below expected)\n"
        f"Cash runway: {metrics['cash_runway_months']} months\n"
        f"CSAT: {metrics['customer_satisfaction']}/5.0 | "
        f"NPS: {metrics['nps_score']}\n"
        "Recommended action: prioritize pipeline acceleration, customer save plan, "
        "inventory rebalance, and cash protection."
    )

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"Enterprise Digital COO - FY {fy}"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Revenue*\n${metrics['revenue']:,.0f}"},
                {
                    "type": "mrkdwn",
                    "text": f"*Revenue Gap*\n-{metrics['revenue_gap_pct']}%",
                },
                {"type": "mrkdwn", "text": f"*Cash Runway*\n{metrics['cash_runway_months']} months"},
                {
                    "type": "mrkdwn",
                    "text": (
                        f"*Customer Health*\nCSAT {metrics['customer_satisfaction']}/5.0, "
                        f"NPS {metrics['nps_score']}"
                    ),
                },
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*Recommended action:* prioritize pipeline acceleration, customer save plan, "
                    "inventory rebalance, and cash protection."
                ),
            },
        },
    ]

    try:
        result = await slack_service.send_message(text, blocks=blocks)
        return {"sent": True, **result, "timestamp": datetime.now().isoformat()}
    except Exception as exc:
        raise _slack_error(exc)

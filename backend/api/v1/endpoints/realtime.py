"""Secure WebRTC handshake for the OpenAI Realtime API."""

import json

import httpx
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import Response

from config import settings


router = APIRouter()


@router.post("/call")
async def create_realtime_call(sdp: str = Body(..., media_type="application/sdp")) -> Response:
    """Exchange a browser SDP offer for an OpenAI WebRTC SDP answer."""
    api_key = settings.OPENAI_API_KEY.strip()
    if not api_key or api_key == "your-openai-api-key":
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")

    session = {
        "type": "realtime",
        "model": "gpt-realtime",
        "instructions": (
            "You are the Enterprise Digital COO voice assistant. Be warm, concise, "
            "and conversational. Explain business insights clearly and ask one useful "
            "follow-up question when appropriate."
        ),
        "output_modalities": ["audio"],
        "audio": {
            "input": {
                "noise_reduction": {"type": "near_field"},
                "transcription": {"model": "gpt-4o-mini-transcribe"},
                "turn_detection": {
                    "type": "semantic_vad",
                    "eagerness": "medium",
                    "create_response": True,
                    "interrupt_response": True,
                },
            },
            "output": {"voice": "marin", "speed": 1.0},
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            upstream = await client.post(
                "https://api.openai.com/v1/realtime/calls",
                headers={"Authorization": f"Bearer {api_key}"},
                files={
                    "sdp": (None, sdp, "application/sdp"),
                    "session": (None, json.dumps(session), "application/json"),
                },
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Could not connect to OpenAI Realtime") from exc

    if upstream.status_code >= 400:
        detail = upstream.text[:500] or "OpenAI Realtime handshake failed"
        raise HTTPException(status_code=upstream.status_code, detail=detail)
    return Response(content=upstream.content, media_type="application/sdp")

"""Secure WebRTC handshake for the OpenAI Realtime API."""

import json

import httpx
from fastapi import APIRouter, Body, File, HTTPException, UploadFile
from fastapi.responses import Response

from config import settings


router = APIRouter()


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)) -> dict:
    """Transcribe compose-box microphone audio with OpenAI instead of browser speech recognition."""
    api_key = settings.OPENAI_API_KEY.strip()
    if not api_key or api_key == "your-openai-api-key":
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
    audio = await file.read()
    if not audio:
        raise HTTPException(status_code=400, detail="Audio is required")
    if len(audio) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio recording is too large")
    filename = file.filename or "recording.webm"
    content_type = file.content_type or "audio/webm"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            upstream = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                data={"model": "gpt-4o-mini-transcribe", "response_format": "json"},
                files={"file": (filename, audio, content_type)},
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Could not connect to OpenAI transcription") from exc
    if upstream.status_code >= 400:
        raise HTTPException(status_code=upstream.status_code, detail=upstream.text[:500])
    payload = upstream.json()
    return {"text": str(payload.get("text", "")).strip()}


@router.post("/speech")
async def create_speech(payload: dict = Body(...)) -> Response:
    """Convert an AI text response to natural OpenAI speech without exposing the API key."""
    api_key = settings.OPENAI_API_KEY.strip()
    if not api_key or api_key == "your-openai-api-key":
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    text = text[:6000]
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            upstream = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini-tts",
                    "voice": "coral",
                    "input": text,
                    "instructions": "Speak clearly, warmly, and confidently like an executive COO assistant.",
                    "response_format": "mp3",
                },
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Could not connect to OpenAI speech") from exc
    if upstream.status_code >= 400:
        raise HTTPException(status_code=upstream.status_code, detail=upstream.text[:500])
    return Response(content=upstream.content, media_type="audio/mpeg")


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

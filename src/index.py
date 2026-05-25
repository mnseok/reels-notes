from __future__ import annotations

import json
import logging

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from .config import get_meta_app_secret, get_meta_verify_token, should_debug_log_raw_payload
from .instagram_parser import extract_shared_reels
from .security import verify_meta_signature


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("instagram_webhook")

app = FastAPI()


@app.get("/")
async def healthcheck() -> dict[str, bool]:
    return {"ok": True}


@app.get("/webhooks/instagram")
async def verify_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    try:
        verify_token = get_meta_verify_token()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if hub_mode == "subscribe" and hub_verify_token == verify_token and hub_challenge is not None:
        return PlainTextResponse(str(hub_challenge))

    raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/webhooks/instagram")
async def receive_webhook(request: Request):
    try:
        app_secret = get_meta_app_secret()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    raw_body = await request.body()
    signature_header = request.headers.get("x-hub-signature-256")
    if not verify_meta_signature(raw_body, signature_header, app_secret):
        raise HTTPException(status_code=403, detail="Forbidden")

    if should_debug_log_raw_payload():
        logger.info(
            json.dumps(
                {
                    "event": "instagram_webhook_raw_payload",
                    "raw_payload": raw_body.decode("utf-8", errors="replace"),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    reels = extract_shared_reels(payload)
    logger.info(
        json.dumps(
            {
                "event": "instagram_webhook_received",
                "entry_count": len(payload.get("entry", [])) if isinstance(payload, dict) else 0,
                "reel_count": len(reels),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )

    return JSONResponse({"ok": True, "reel_count": len(reels)})

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse, urlunparse


ALLOWED_INSTAGRAM_HOSTS = {"instagram.com", "www.instagram.com"}
REEL_PATH_RE = re.compile(r"^/reel/([A-Za-z0-9_-]+)/?$")
TEXT_REEL_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?instagram\.com/reel/[A-Za-z0-9_-]+(?:/)?(?:[?#][^\s\"'<>]*)?"
)


def extract_shared_reels(payload: dict) -> list[dict]:
    if not isinstance(payload, dict):
        return []

    results: list[dict] = []
    seen: set[tuple[str, str]] = set()

    entries = payload.get("entry")
    if not isinstance(entries, list):
        return []

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        source_ig_account_id = _as_str(entry.get("id") or entry.get("account_id") or entry.get("ig_account_id"))
        messaging_items = entry.get("messaging")
        if not isinstance(messaging_items, list):
            continue

        for messaging in messaging_items:
            if not isinstance(messaging, dict):
                continue

            sender_id = _nested_id(messaging.get("sender"))
            recipient_id = _nested_id(messaging.get("recipient"))
            message = messaging.get("message")
            if not isinstance(message, dict):
                continue

            message_id = _as_str(message.get("mid") or message.get("message_id"))
            if not message_id:
                continue

            reel_candidates: list[dict[str, Any]] = []

            attachments = message.get("attachments")
            if isinstance(attachments, list):
                for attachment in attachments:
                    if not isinstance(attachment, dict):
                        continue
                    attachment_type = _as_str(attachment.get("type"))
                    if attachment_type not in {"ig_reel", "reel"}:
                        continue
                    payload_block = attachment.get("payload")
                    if not isinstance(payload_block, dict):
                        continue
                    reel_url = _normalize_reel_url(payload_block.get("url"))
                    if not reel_url:
                        continue
                    reel_candidates.append(
                        {
                            "attachment_type": attachment_type,
                            "reel_url": reel_url,
                            "reel_video_id": _as_str(
                                payload_block.get("video_id")
                                or payload_block.get("media_id")
                                or payload_block.get("id")
                            ),
                            "reel_title": _as_str(
                                payload_block.get("title")
                                or payload_block.get("name")
                                or payload_block.get("text")
                            ),
                        }
                    )

            shares = message.get("shares")
            if isinstance(shares, dict):
                share_data = shares.get("data")
                if isinstance(share_data, list):
                    for share in share_data:
                        if not isinstance(share, dict):
                            continue
                        reel_url = _normalize_reel_url(share.get("link"))
                        if not reel_url:
                            continue
                        reel_candidates.append(
                            {
                                "attachment_type": "share_link",
                                "reel_url": reel_url,
                                "reel_video_id": _as_str(
                                    share.get("video_id")
                                    or share.get("media_id")
                                    or share.get("id")
                                ),
                                "reel_title": _as_str(
                                    share.get("title")
                                    or share.get("name")
                                    or share.get("text")
                                ),
                            }
                        )

            text = message.get("text")
            if isinstance(text, str):
                for match in TEXT_REEL_URL_RE.finditer(text):
                    reel_url = _normalize_reel_url(match.group(0))
                    if not reel_url:
                        continue
                    reel_candidates.append(
                        {
                            "attachment_type": "text_url",
                            "reel_url": reel_url,
                            "reel_video_id": None,
                            "reel_title": None,
                        }
                    )

            for candidate in reel_candidates:
                dedupe_key = (message_id, candidate["reel_url"])
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                results.append(
                    {
                        "source_ig_account_id": source_ig_account_id,
                        "sender_id": sender_id,
                        "recipient_id": recipient_id,
                        "message_id": message_id,
                        "reel_url": candidate["reel_url"],
                        "reel_video_id": candidate["reel_video_id"],
                        "reel_title": candidate["reel_title"],
                        "attachment_type": candidate["attachment_type"],
                    }
                )

    return results


def _normalize_reel_url(raw_url: Any) -> str | None:
    url = _as_str(raw_url)
    if not url:
        return None
    normalized_input = url
    if normalized_input.startswith(("instagram.com/", "www.instagram.com/")):
        normalized_input = "https://" + normalized_input

    parsed = urlparse(normalized_input)
    if parsed.scheme not in {"http", "https"}:
        return None

    host = parsed.netloc.lower()
    if host not in ALLOWED_INSTAGRAM_HOSTS:
        return None

    match = REEL_PATH_RE.match(parsed.path or "")
    if not match:
        return None

    shortcode = match.group(1)
    return urlunparse((parsed.scheme, host, f"/reel/{shortcode}/", "", "", ""))


def _nested_id(value: Any) -> str | None:
    if isinstance(value, dict):
        return _as_str(value.get("id"))
    return _as_str(value)


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return str(value)


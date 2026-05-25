from __future__ import annotations

import hashlib
import hmac


def verify_meta_signature(raw_body: bytes, signature_header: str | None, app_secret: str) -> bool:
    if not app_secret or not app_secret.strip():
        return False
    if not isinstance(raw_body, (bytes, bytearray)):
        return False
    if not signature_header:
        return False

    header = signature_header.strip()
    prefix, separator, value = header.partition("=")
    if prefix != "sha256" or separator != "=" or not value:
        return False

    signature = value.strip().lower()
    if len(signature) != 64:
        return False
    if any(char not in "0123456789abcdef" for char in signature):
        return False

    expected = hmac.new(
        app_secret.encode("utf-8"),
        bytes(raw_body),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


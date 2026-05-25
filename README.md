# Instagram Webhook Backend

Minimal FastAPI backend for testing an Instagram Webhook callback on Vercel.

## Purpose

This service only handles:

- Webhook verification
- Webhook POST reception
- Meta signature verification
- Defensive payload parsing
- Shared Reels URL extraction
- Unit tests

## Non-Goals

- No Instagram login scraping
- No DM polling
- No Reels video downloading
- No `yt-dlp`
- No browser automation
- No unofficial Instagram scraping

## Local Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file from the example:

```bash
copy .env.example .env
```

Set the required values in `.env`:

- `META_VERIFY_TOKEN`
- `META_APP_SECRET`
- `DEBUG_LOG_RAW_PAYLOAD`

Run the app:

```bash
python -m uvicorn src.index:app --host 0.0.0.0 --port 8000
```

Run tests:

```bash
pytest
```

## Vercel Deployment

This project is laid out for Vercel's FastAPI support using `src/index.py` with `app = FastAPI()`.

No `vercel.json` is required for the current FastAPI convention.

Required Vercel environment variables:

- `META_VERIFY_TOKEN`
- `META_APP_SECRET`
- `DEBUG_LOG_RAW_PAYLOAD`

Callback URL format:

```text
https://<vercel-domain>/webhooks/instagram
```

## Endpoints

- `GET /` returns a simple health JSON response.
- `GET /webhooks/instagram` handles Meta webhook verification.
- `POST /webhooks/instagram` verifies the Meta signature, parses the payload, and returns a reel count.

## Verification Checklist

- `GET /` works
- `GET /webhooks/instagram` returns `hub.challenge` when the token matches
- `POST /webhooks/instagram` rejects invalid signatures
- Parser tests pass

## Manual Meta Dashboard Steps

You still need to configure these in the Meta Developer Dashboard:

- Webhook callback URL
- Verify token
- App secret
- Subscription fields for the Instagram webhook you want to receive


# ProofPilot

ProofPilot turns an ambiguous goal into a short action plan where every step has explicit evidence and a risk note. It is designed for people who need to know not only *what to do*, but also *how to verify that it worked*.

## Why it is different

Routine task agents usually optimize for execution. ProofPilot optimizes for trustworthy progress: define the finish line, collect inputs, execute a small step, verify the result, and leave an audit-friendly summary.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python web.py
```

Open http://127.0.0.1:8080 and enter a goal. Without an API key it uses a deterministic fallback, so the demo is reproducible. To use Gemini, set `GEMINI_API_KEY`; the app sends the planning prompt to Gemini 2.5 Flash and validates the JSON response before showing it.

## Deploy to Cloud Run

```bash
gcloud run deploy proofpilot --source . --region us-central1 --allow-unauthenticated
```

Set `GEMINI_API_KEY` in the Cloud Run service environment only if you want model-backed plans; the deterministic fallback works without it.

## API

- `GET /health` returns `{"ok": true}`.
- `POST /api/plan` with `{"goal":"..."}` returns five steps with `action`, `evidence`, and `risk`.

## Hackathon fit

ProofPilot is a new AI-powered productivity and decision-support application for the AI Builders Hackathon. It targets a common problem: people lose confidence in plans when outcomes cannot be verified. The project includes a public repository, reproducible setup instructions, a live web demo, and an architecture diagram.

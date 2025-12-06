# Voice of the Customer Backend

FastAPI service that serves two purposes:

1. **Reddit ingestion sandbox** for exploring bank-related conversations.
2. **Synthetic LLM insights API** used by the Flutter front-end to render graphs and lists without live data dependencies.

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints (selection)

- `GET /health` – health check
- `GET /reddit/{subreddit}?sort=hot|new|top|rising&time_filter=day&limit=20`
- `GET /llm/banking-insights` – returns `app/fake_llm_data.json` with synthetic analysis covering sentiment, demand trends, and top requests
- `GET /reddit/ml-data` – bulk export formatted for downstream analytics
- `GET /data/status` – sanity check on saved scrape output

Example:

```bash
curl "http://127.0.0.1:8000/reddit/flutterdev?sort=top&time_filter=week&limit=10"
```

CORS is open to simplify local testing and Flutter web integration.

## Notes

- Synthetic data lives at `app/fake_llm_data.json`; update it to drive different UI states.
- Reddit public JSON scraping can break if Reddit changes responses or rate-limits aggressively.



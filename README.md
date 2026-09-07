# News Aggregator Platform

A real-time news aggregation system that pulls headlines from multiple public
RSS sources, normalizes them into a single feed, and serves them through a
REST API to a React frontend with search and source filtering.

## Tech Stack

- **Backend:** Python, Flask, `feedparser`
- **Frontend:** React, Vite

## Features

- Aggregates articles from 4 independent public RSS feeds (BBC World, NPR,
  The Guardian, Hacker News) with no API key required
- In-memory caching per source with a 5-minute TTL, so the same feed isn't
  re-fetched on every request — keeps response times low and is polite to
  upstream sources
- REST endpoints for listing sources, searching by keyword, and filtering by
  source
- React frontend with live search, a source dropdown, and responsive article
  cards linking back to the original article

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/health | Liveness check |
| GET | /api/sources | List configured source keys |
| GET | /api/news | List articles. Query params: source, q, limit |

Example:

```bash
curl "http://localhost:5000/api/news?source=bbc-world&q=economy&limit=10"
```

## Running locally

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API runs on http://localhost:5000.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies /api requests to the Flask backend (see vite.config.js).

### Tests

```bash
cd backend
pip install pytest
pytest
```

## Project structure

```
news-aggregator-platform/
├── backend/
│   ├── app.py            # Flask API + in-memory cache
│   ├── requirements.txt
│   └── tests/
│       └── test_app.py
└── frontend/
    ├── src/
    │   ├── App.jsx        # Main UI: search, filter, article list
    │   └── main.jsx
    └── package.json
```

"""
News Aggregator Platform — backend
A Flask REST API that aggregates and normalizes articles from multiple
public RSS news sources, with in-memory caching, search, and source
filtering.
"""
from __future__ import annotations

import time
import threading
from dataclasses import dataclass, asdict
from typing import List, Optional

import feedparser
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Configuration -----------------------------------------------------

# Public RSS feeds — no API key required. Add/remove sources here.
SOURCES = {
    "bbc-world": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "npr-news": "https://feeds.npr.org/1001/rss.xml",
    "guardian-world": "https://www.theguardian.com/world/rss",
    "hacker-news": "https://hnrss.org/frontpage",
}

CACHE_TTL_SECONDS = 5 * 60  # refresh each source at most every 5 minutes


# --- Data model ----------------------------------------------------------

@dataclass
class Article:
    id: str
    source: str
    title: str
    link: str
    summary: str
    published: Optional[str]


# --- In-memory cache with a background refresh lock -----------------------

class NewsCache:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._articles: List[Article] = []
        self._last_fetched: dict[str, float] = {}

    def _fetch_source(self, source_key: str, url: str) -> List[Article]:
        parsed = feedparser.parse(url)
        articles = []
        for entry in parsed.entries[:30]:
            articles.append(
                Article(
                    id=f"{source_key}:{entry.get('id', entry.get('link', entry.get('title', '')))}",
                    source=source_key,
                    title=entry.get("title", "(untitled)"),
                    link=entry.get("link", ""),
                    summary=(entry.get("summary", "") or "")[:400],
                    published=entry.get("published", None),
                )
            )
        return articles

    def refresh_if_stale(self) -> None:
        now = time.time()
        with self._lock:
            stale_sources = [
                key
                for key, url in SOURCES.items()
                if now - self._last_fetched.get(key, 0) > CACHE_TTL_SECONDS
            ]

        for key in stale_sources:
            try:
                fetched = self._fetch_source(key, SOURCES[key])
            except Exception as exc:  # network hiccups shouldn't crash the API
                app.logger.warning("Failed to fetch %s: %s", key, exc)
                continue

            with self._lock:
                self._articles = [a for a in self._articles if a.source != key] + fetched
                self._last_fetched[key] = now

    def get_articles(
        self, source: Optional[str] = None, query: Optional[str] = None
    ) -> List[Article]:
        self.refresh_if_stale()
        with self._lock:
            results = list(self._articles)

        if source:
            results = [a for a in results if a.source == source]

        if query:
            q = query.lower()
            results = [
                a for a in results if q in a.title.lower() or q in a.summary.lower()
            ]

        return results


cache = NewsCache()


# --- Routes ----------------------------------------------------------------

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/sources")
def sources():
    return jsonify({"sources": list(SOURCES.keys())})


@app.get("/api/news")
def news():
    source = request.args.get("source")
    query = request.args.get("q")
    limit = request.args.get("limit", default=50, type=int)

    if source and source not in SOURCES:
        return jsonify({"error": f"unknown source '{source}'"}), 400

    articles = cache.get_articles(source=source, query=query)
    articles.sort(key=lambda a: a.published or "", reverse=True)

    return jsonify(
        {
            "count": len(articles[:limit]),
            "total": len(articles),
            "articles": [asdict(a) for a in articles[:limit]],
        }
    )


if __name__ == "__main__":
    # Warm the cache once on startup so the first request isn't empty.
    cache.refresh_if_stale()
    app.run(host="0.0.0.0", port=5000, debug=True)

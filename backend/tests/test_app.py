import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as app_module


def test_health():
    client = app_module.app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_sources_lists_configured_feeds():
    client = app_module.app.test_client()
    resp = client.get("/api/sources")
    data = resp.get_json()
    assert set(data["sources"]) == set(app_module.SOURCES.keys())


def test_news_rejects_unknown_source():
    client = app_module.app.test_client()
    resp = client.get("/api/news?source=not-a-real-source")
    assert resp.status_code == 400


def test_cache_filters_by_query():
    cache = app_module.NewsCache()
    cache._articles = [
        app_module.Article("a1", "bbc-world", "Markets rally", "http://x", "stocks up", None),
        app_module.Article("a2", "bbc-world", "Weather update", "http://y", "rain expected", None),
    ]
    cache._last_fetched = {k: 10**12 for k in app_module.SOURCES}  # pretend fresh

    results = cache.get_articles(query="market")
    assert len(results) == 1
    assert results[0].id == "a1"

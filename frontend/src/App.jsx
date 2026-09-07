import { useEffect, useMemo, useState } from "react";

const SOURCE_LABELS = {
  "bbc-world": "BBC World",
  "npr-news": "NPR News",
  "guardian-world": "The Guardian",
  "hacker-news": "Hacker News",
};

export default function App() {
  const [articles, setArticles] = useState([]);
  const [sources, setSources] = useState([]);
  const [activeSource, setActiveSource] = useState("");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/sources")
      .then((r) => r.json())
      .then((data) => setSources(data.sources))
      .catch(() => {});
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    if (activeSource) params.set("source", activeSource);
    if (query) params.set("q", query);

    setLoading(true);
    setError(null);

    fetch(`/api/news?${params.toString()}`)
      .then((r) => {
        if (!r.ok) throw new Error(`Request failed: ${r.status}`);
        return r.json();
      })
      .then((data) => setArticles(data.articles))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [activeSource, query]);

  const sourceOptions = useMemo(
    () => [{ key: "", label: "All sources" }, ...sources.map((s) => ({ key: s, label: SOURCE_LABELS[s] || s }))],
    [sources]
  );

  return (
    <div style={{ maxWidth: 780, margin: "0 auto", padding: "24px", fontFamily: "system-ui, sans-serif" }}>
      <h1>📰 News Aggregator</h1>
      <p style={{ color: "#555" }}>Live headlines pulled from multiple public news sources.</p>

      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <input
          type="text"
          placeholder="Search headlines…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ flex: 1, minWidth: 200, padding: "8px 12px" }}
        />
        <select value={activeSource} onChange={(e) => setActiveSource(e.target.value)} style={{ padding: "8px 12px" }}>
          {sourceOptions.map((opt) => (
            <option key={opt.key} value={opt.key}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {loading && <p>Loading…</p>}
      {error && <p style={{ color: "crimson" }}>Error: {error}</p>}

      <ul style={{ listStyle: "none", padding: 0 }}>
        {articles.map((a) => (
          <li key={a.id} style={{ borderBottom: "1px solid #eee", padding: "12px 0" }}>
            <a href={a.link} target="_blank" rel="noreferrer" style={{ fontWeight: 600 }}>
              {a.title}
            </a>
            <div style={{ fontSize: 12, color: "#888", margin: "4px 0" }}>
              {SOURCE_LABELS[a.source] || a.source} {a.published ? `· ${a.published}` : ""}
            </div>
            <p style={{ margin: 0, color: "#333" }}>{a.summary}</p>
          </li>
        ))}
      </ul>

      {!loading && !error && articles.length === 0 && <p>No articles match your filters.</p>}
    </div>
  );
}

"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function scoreColor(score) {
  if (score < 40) return "#e53935";
  if (score < 70) return "#fbc02d";
  return "#43a047";
}

function ProgressBar({ score }) {
  const color = scoreColor(score);
  return (
    <div className="bar-wrapper">
      <div className="bar-fill" style={{ width: `${score}%`, background: color }} />
      <span className="bar-label">{score}/100</span>
    </div>
  );
}

export default function HomePage() {
  const [filters, setFilters] = useState({
    language: "python",
    location: "",
    limit: 10,
    min_followers: 5,
    min_repos: 3,
    min_account_age_days: 180,
    exclude_companies: "Meta, Google"
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [candidates, setCandidates] = useState([]);

  const searchCandidates = async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      params.set("language", filters.language);
      if (filters.location.trim()) params.set("location", filters.location.trim());
      params.set("limit", String(filters.limit));
      params.set("min_followers", String(filters.min_followers));
      params.set("min_repos", String(filters.min_repos));
      params.set("min_account_age_days", String(filters.min_account_age_days));

      filters.exclude_companies
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean)
        .forEach((company) => params.append("exclude_companies", company));

      const response = await fetch(`${API_URL}/search?${params.toString()}`);
      if (!response.ok) {
        throw new Error("Ошибка запроса к backend");
      }
      const data = await response.json();
      setCandidates(data.candidates || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container">
      <h1>GitHub Talent Finder</h1>
      <p>Красный = низкая перспектива, зеленый = кандидат для оффера.</p>

      <div className="filters">
        <input value={filters.language} onChange={(e) => setFilters({ ...filters, language: e.target.value })} placeholder="Язык" />
        <input value={filters.location} onChange={(e) => setFilters({ ...filters, location: e.target.value })} placeholder="Локация" />
        <input type="number" value={filters.limit} onChange={(e) => setFilters({ ...filters, limit: Number(e.target.value) })} placeholder="Лимит" />
        <input type="number" value={filters.min_followers} onChange={(e) => setFilters({ ...filters, min_followers: Number(e.target.value) })} placeholder="Мин. подписчики" />
        <input type="number" value={filters.min_repos} onChange={(e) => setFilters({ ...filters, min_repos: Number(e.target.value) })} placeholder="Мин. репозитории" />
        <input type="number" value={filters.min_account_age_days} onChange={(e) => setFilters({ ...filters, min_account_age_days: Number(e.target.value) })} placeholder="Возраст аккаунта, дни" />
        <input value={filters.exclude_companies} onChange={(e) => setFilters({ ...filters, exclude_companies: e.target.value })} placeholder="Исключить компании (через запятую)" />
        <button onClick={searchCandidates} disabled={loading}>
          {loading ? "Поиск..." : "Найти кандидатов"}
        </button>
      </div>

      {error ? <p className="error">{error}</p> : null}

      <div className="cards">
        {candidates.map((candidate) => (
          <div className="card" key={candidate.id}>
            <div className="card-header">
              <img src={candidate.avatar_url} alt={candidate.username} />
              <div>
                <h3>
                  {candidate.name || candidate.username}
                </h3>
                <a href={candidate.profile_url} target="_blank" rel="noreferrer">
                  @{candidate.username}
                </a>
              </div>
            </div>

            <ProgressBar score={candidate.prospect_score} />

            <p>{candidate.bio || "Био отсутствует"}</p>
            <p><strong>Компания:</strong> {candidate.company || "Не указана"}</p>
            <p><strong>Подписчики:</strong> {candidate.followers}</p>
            <p><strong>Репозитории:</strong> {candidate.public_repos}</p>
            <p><strong>Звёзды:</strong> {candidate.total_stars}</p>
            <p><strong>Активные репо (6 мес):</strong> {candidate.active_repos_6m}</p>
          </div>
        ))}
      </div>
    </main>
  );
}

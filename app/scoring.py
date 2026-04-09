from datetime import datetime, timezone
from math import log10


def _to_datetime(ts: str):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def build_candidate_scores(profile: dict, repos: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    created_at = _to_datetime(profile["created_at"])
    account_age_days = max((now - created_at).days, 1)

    followers = profile.get("followers", 0)
    public_repos = profile.get("public_repos", 0)
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)

    active_repos_6m = 0
    language_set = set()
    for repo in repos:
        pushed_at = repo.get("pushed_at")
        if pushed_at:
            delta_days = (now - _to_datetime(pushed_at)).days
            if delta_days <= 180:
                active_repos_6m += 1
        if repo.get("language"):
            language_set.add(repo["language"])

    languages_count = len(language_set)
    avg_stars_per_repo = total_stars / max(len(repos), 1)
    active_ratio = active_repos_6m / max(len(repos), 1)

    # Формула перспективности (0-100):
    # 25% социальный сигнал (followers),
    # 25% качество проектов (stars),
    # 20% активность за 6 месяцев,
    # 15% стабильность аккаунта (возраст),
    # 15% разнообразие стеков.
    social_score = clamp(log10(followers + 1) / 3, 0, 1) * 100
    quality_score = clamp(log10(avg_stars_per_repo + 1) / 2, 0, 1) * 100
    activity_score = clamp(active_ratio, 0, 1) * 100
    stability_score = clamp(account_age_days / 3650, 0, 1) * 100
    breadth_score = clamp(languages_count / 8, 0, 1) * 100

    weighted = (
        social_score * 0.25
        + quality_score * 0.25
        + activity_score * 0.20
        + stability_score * 0.15
        + breadth_score * 0.15
    )

    prospect_score = int(round(clamp(weighted, 0, 100)))

    return {
        "prospect_score": prospect_score,
        "total_stars": total_stars,
        "active_repos_6m": active_repos_6m,
        "languages_count": languages_count,
        "account_age_days": account_age_days,
        "score_breakdown": {
            "social_score": round(social_score, 1),
            "quality_score": round(quality_score, 1),
            "activity_score": round(activity_score, 1),
            "stability_score": round(stability_score, 1),
            "breadth_score": round(breadth_score, 1),
        },
        "public_repos": public_repos,
    }

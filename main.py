from datetime import datetime, timezone
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.data_base import Base, SessionLocal, engine
from app.github_client import build_search_query, get_user_info, get_user_repos, search_users
from app.models import Candidate
from app.scoring import build_candidate_scores
from app.schemas import CandidateOut, HealthResponse, SearchResponse

app = FastAPI(
    title="AI Talent API",
    description="Поиск перспективных GitHub-кандидатов с сохранением в PostgreSQL",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _is_excluded_company(company: Optional[str], excluded_companies: List[str]) -> bool:
    if not company or not excluded_companies:
        return False
    normalized_company = company.lower().strip()
    return any(word.lower().strip() in normalized_company for word in excluded_companies if word.strip())


def _is_too_new(created_at: str, min_account_age_days: int) -> bool:
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    age_days = (datetime.now(timezone.utc) - created).days
    return age_days < min_account_age_days


@app.get("/", response_model=HealthResponse)
def root():
    return HealthResponse(
        status="ok",
        api_version="2.0.0",
        database="postgresql",
    )


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        api_version="2.0.0",
        database="postgresql",
    )


@app.get("/search", response_model=SearchResponse)
def search_candidates(
    language: str = Query("python", description="Язык программирования"),
    location: Optional[str] = Query(None, description="Локация"),
    limit: int = Query(20, ge=1, le=50, description="Сколько кандидатов вернуть"),
    min_followers: int = Query(5, ge=0),
    min_repos: int = Query(3, ge=0),
    min_account_age_days: int = Query(180, ge=0),
    exclude_companies: List[str] = Query(default=[]),
    db: Session = Depends(get_db),
):
    query = build_search_query(language=language, location=location)
    users = search_users(query=query, per_page=limit * 2)

    if not users:
        raise HTTPException(status_code=404, detail="Кандидаты не найдены")

    accepted = []
    skipped = 0

    for user in users:
        username = user["login"]
        profile = get_user_info(username)
        repos = get_user_repos(username, max_repos=60)

        if not profile:
            skipped += 1
            continue
        if _is_excluded_company(profile.get("company"), exclude_companies):
            skipped += 1
            continue
        if _is_too_new(profile.get("created_at"), min_account_age_days):
            skipped += 1
            continue
        if profile.get("followers", 0) < min_followers:
            skipped += 1
            continue
        if profile.get("public_repos", 0) < min_repos:
            skipped += 1
            continue

        score_data = build_candidate_scores(profile=profile, repos=repos)
        candidate_payload = {
            "username": profile.get("login"),
            "name": profile.get("name"),
            "profile_url": profile.get("html_url"),
            "avatar_url": profile.get("avatar_url"),
            "bio": profile.get("bio"),
            "company": profile.get("company"),
            "location": profile.get("location"),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
            "public_repos": profile.get("public_repos", 0),
            "total_stars": score_data["total_stars"],
            "active_repos_6m": score_data["active_repos_6m"],
            "languages_count": score_data["languages_count"],
            "account_age_days": score_data["account_age_days"],
            "prospect_score": score_data["prospect_score"],
            "score_breakdown": score_data["score_breakdown"],
        }

        existing = db.query(Candidate).filter(Candidate.username == username).one_or_none()
        if existing:
            for key, value in candidate_payload.items():
                setattr(existing, key, value)
            db.add(existing)
            stored = existing
        else:
            stored = Candidate(**candidate_payload)
            db.add(stored)

        db.flush()
        accepted.append(stored)
        if len(accepted) >= limit:
            break

    db.commit()

    return SearchResponse(
        query=query,
        requested=limit,
        found=len(accepted),
        skipped=skipped,
        candidates=accepted,
    )


@app.get("/candidates", response_model=List[CandidateOut])
def list_candidates(
    min_score: int = Query(0, ge=0, le=100),
    db: Session = Depends(get_db),
):
    return (
        db.query(Candidate)
        .filter(Candidate.prospect_score >= min_score)
        .order_by(Candidate.prospect_score.desc())
        .all()
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

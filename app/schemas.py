from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    api_version: str
    database: str


class CandidateOut(BaseModel):
    id: int
    username: str
    name: Optional[str]
    profile_url: str
    avatar_url: Optional[str]
    bio: Optional[str]
    company: Optional[str]
    location: Optional[str]
    followers: int
    following: int
    public_repos: int
    total_stars: int
    active_repos_6m: int
    languages_count: int
    account_age_days: int
    prospect_score: int
    score_breakdown: dict
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    query: str
    requested: int
    found: int
    skipped: int
    candidates: List[CandidateOut]

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.data_base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_url: Mapped[str] = mapped_column(String(512), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    followers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    following: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    public_repos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_stars: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_repos_6m: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    languages_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    account_age_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    prospect_score: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    score_breakdown: Mapped[dict] = mapped_column(JSON, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
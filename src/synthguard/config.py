"""Process configuration. No secrets are required for Phase 0."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field

from synthguard import DEFAULT_IDENTITY_THRESHOLD, MIN_SCREENABLE_LENGTH


class Settings(BaseModel):
    env: str = Field(default="dev")
    repo_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2])
    pretty_logs: bool = True
    min_length: int = MIN_SCREENABLE_LENGTH
    identity_threshold: float = DEFAULT_IDENTITY_THRESHOLD

    @property
    def sample_dir(self) -> Path:
        return self.repo_root / "data" / "sample"

    @property
    def research_dir(self) -> Path:
        return self.repo_root / "research" / "phase0"

    @property
    def split_order_dir(self) -> Path:
        return self.sample_dir / "split-orders"


def get_settings() -> Settings:
    return Settings(
        env=os.environ.get("SYNTHGUARD_ENV", "dev"),
        pretty_logs=os.environ.get("SYNTHGUARD_ENV", "dev") != "prod",
    )

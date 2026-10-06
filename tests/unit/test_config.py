from __future__ import annotations

from synthguard.config import get_settings
from synthguard.logging import configure_logging


def test_settings_point_at_sample_dir() -> None:
    settings = get_settings()
    assert settings.sample_dir.name == "sample"
    assert settings.min_length == 50
    assert settings.identity_threshold == 0.90
    assert (settings.research_dir / "run_all.py").is_file()
    assert settings.split_order_dir == settings.sample_dir / "split-orders"


def test_configure_logging_does_not_raise() -> None:
    configure_logging()


def test_configure_logging_json(monkeypatch: object) -> None:
    monkeypatch.setenv("SYNTHGUARD_ENV", "prod")  # type: ignore[attr-defined]
    configure_logging()

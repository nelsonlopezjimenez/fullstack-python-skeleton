"""app/config.py (Chapter 3: tests/2-config.test.js). No database needed."""
import pytest
from pydantic import ValidationError

from app.config import DEV_SECRET, Settings


# [BEGINNER] Keyword arguments override the environment; _env_file=None ignores a local .env,
# so the tests give the same result on every machine.
def test_production_refuses_the_development_secret():
    with pytest.raises(ValidationError, match="JWT_SECRET must be set in production"):
        Settings(_env_file=None, env="production", jwt_secret=DEV_SECRET)


def test_production_starts_with_a_real_secret():
    settings = Settings(_env_file=None, env="production", jwt_secret="a-real-secret")
    assert settings.is_production


def test_cors_origins_are_split_and_trimmed():
    settings = Settings(_env_file=None, cors_origin=" http://a.io , ,http://b.io")
    assert settings.cors_origins == ["http://a.io", "http://b.io"]


def test_cors_is_off_by_default():
    assert Settings(_env_file=None, cors_origin="").cors_origins == []


def test_port_is_converted_to_int(monkeypatch):
    # [BEGINNER] monkeypatch.setenv changes an environment variable for this test only.
    monkeypatch.setenv("PORT", "8123")
    assert Settings(_env_file=None).port == 8123

import os
import pytest

def get_backend_url():
    return os.getenv("BACKEND_URL", "http://localhost:8000")

def test_get_backend_url_default(monkeypatch):
    monkeypatch.delenv("BACKEND_URL", raising=False)
    assert get_backend_url() == "http://localhost:8000"

def test_get_backend_url_custom(monkeypatch):
    monkeypatch.setenv("BACKEND_URL", "https://myapi.com")
    assert get_backend_url() == "https://myapi.com"

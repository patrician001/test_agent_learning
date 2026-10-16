from unittest.mock import MagicMock

import pytest
import requests

from repostats import fetch_text


def make_get(monkeypatch, response):
    get = MagicMock(return_value=response)
    monkeypatch.setattr(requests, "get", get)
    return get


def test_returns_body_text(monkeypatch):
    make_get(monkeypatch, MagicMock(text="body"))
    assert fetch_text("https://example.invalid/a") == "body"


def test_default_timeout(monkeypatch):
    get = make_get(monkeypatch, MagicMock(text=""))
    fetch_text("https://example.invalid/a")
    get.assert_called_once_with("https://example.invalid/a", timeout=10)


def test_custom_timeout(monkeypatch):
    get = make_get(monkeypatch, MagicMock(text=""))
    fetch_text("https://example.invalid/a", timeout=3)
    get.assert_called_once_with("https://example.invalid/a", timeout=3)


def test_http_error_raises(monkeypatch):
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError("404")
    make_get(monkeypatch, response)
    with pytest.raises(requests.HTTPError):
        fetch_text("https://example.invalid/missing")

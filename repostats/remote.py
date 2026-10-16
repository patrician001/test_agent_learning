"""Download helpers for remote text resources."""

import requests


def fetch_text(url, timeout=10):
    """Download ``url`` and return the response body as text.

    HTTP error statuses raise ``requests.HTTPError``.

    >>> from unittest.mock import MagicMock, patch
    >>> with patch("requests.get", return_value=MagicMock(text="hello")):
    ...     print(fetch_text("https://example.invalid/x"))
    hello
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text

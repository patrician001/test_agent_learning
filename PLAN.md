# Plan: add `repostats.remote.fetch_text`

## Summary
New module `repostats/remote.py` with `fetch_text(url, timeout=10)`, using `requests` (imported at module top).
The owner explicitly accepts the `requests` dependency, which conflicts with CONTRIBUTING rule 4 ("no new
dependencies") and the CI check enforcing it, so those must be updated as part of this change.

## Files
- repostats/remote.py
- repostats/__init__.py
- pyproject.toml
- tests/test_conventions.py
- tests/test_remote.py
- CONTRIBUTING.md
- CHANGELOG.md
- .github/workflows/ci.yml

## Changes
- `repostats/remote.py`: `import requests` at top. `fetch_text(url, timeout=10) -> str`: `requests.get(url,
  timeout=timeout)`, `response.raise_for_status()`, return `response.text`. Docstring with a `>>>` doctest that
  never touches the network: it uses `unittest.mock.patch("requests.get")` (patching the attribute on the
  `requests` module, so it works regardless of import style) returning a mock whose `.text` is e.g. `"hello"`,
  and prints `fetch_text("https://example.invalid/x")`. Also documents that HTTP errors raise
  `requests.HTTPError`.
- `repostats/__init__.py`: import `fetch_text` from `repostats.remote`; add to `__all__` (sorted).
- `pyproject.toml`: `dependencies = ["requests>=2.31"]`.
- `tests/test_conventions.py`: `test_no_dependencies` would now fail. Replace it with a test that dependencies
  are exactly the allowed set (`requests` only), and no `optional-dependencies`; update module docstring.
- `tests/test_remote.py`: unit tests with `unittest.mock`/`monkeypatch` on `requests.get` (no network):
  returns body text, passes the timeout (default 10 and custom), raises on HTTP error status. Convention 1
  (`sample_repo`) applies to on-disk trees; these tests need no files, so the fixture is not used.
- `CONTRIBUTING.md`: amend rule 4 to say the only permitted third-party dependency is `requests` (used by
  `repostats/remote.py`), others still need owner approval.
- `CHANGELOG.md`: under `## Unreleased` add `- Added `fetch_text`, which downloads a URL and returns the body
  as text (adds the `requests` dependency).`
- `.github/workflows/ci.yml`: install `requests` in the pip step (e.g. `pytest==8.3.3 ruff==0.6.9 requests`)
  so import and doctest collection succeed in CI.

## Testing
`ruff check .`, `ruff format --check .`, `pytest --doctest-modules` (needs `requests` installed locally).
Verify the doctest passes with the network unavailable, and `test_every_public_function_has_a_doctest` passes
(importing `repostats.remote` via walk_packages).

## Risks
- Conflict with rule 4 / `test_no_dependencies`: resolved by editing the test and CONTRIBUTING.md; reviewers
  should confirm this scope is intended (owner stated acceptance of the dependency).
- `requests` is now required at `import repostats` time (since `__init__` imports `remote`); users of only the
  file helpers must install it too. Accepted per the goal's top-level import requirement.
- Unpinned `requests` in CI could drift; pin a version if the owner prefers.
- Mock-based doctest relies on patching `requests.get`; the implementation must call `requests.get` (not
  `from requests import get`).

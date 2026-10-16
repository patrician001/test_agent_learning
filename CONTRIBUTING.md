# Contributing

Every change follows these four conventions. Reviews reject a change that misses one.

1. **Tests use the `sample_repo` fixture.** Tests that need files on disk take the `sample_repo` fixture from
   `tests/conftest.py` (extend it if a test needs more files); they do not build their own temporary trees.
2. **Every public function has a doctest.** A function whose name does not start with `_` has a docstring with at
   least one `>>>` example that passes under `pytest --doctest-modules`.
3. **`CHANGELOG.md` gets an entry under `## Unreleased`** for every change in behaviour: one line, starting with
   `Added`, `Changed` or `Fixed`.
4. **No new dependencies.** The package uses the Python standard library, plus `requests` (used by
   `repostats/remote.py`) as the only permitted third-party dependency; `[project] dependencies` lists
   only `requests`. Any other package, or vendored third-party code, needs the owner's approval.

Checks: `ruff check .`, `ruff format --check .` and `pytest --doctest-modules`. CI runs all three on every push.

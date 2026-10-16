# Plan: `largest_files(root, n)`

## Behaviour
`largest_files(root, n)` returns a list of at most `n` `(relative_path, size_bytes)` tuples, largest first, ties broken by
path ascending. Paths use "/" separators and `.git` is skipped, exactly as in `list_files`. `n <= 0` returns `[]`;
`n` larger than the file count returns all files.

## Files to change
1. `repostats/files.py`
   - Add `largest_files(root: str | Path, n: int) -> list[tuple[str, int]]`.
   - Build on `list_files(root)`, so the `.git` skipping and path format stay in one place. Pair each path with
     `(base / path).stat().st_size`, sort by key `(-size, path)`, slice `[:max(n, 0)]`.
   - Add a doctest (needed by CONTRIBUTING rule 2 and enforced by `tests/test_conventions.py`) in the style of the
     existing ones, with a tempdir and two files of different sizes.
   - Update the module docstring only if needed ("Listing and counting..." is close enough; probably leave it).
2. `repostats/__init__.py`: import `largest_files` and add it to `__all__` (keep alphabetical: `count_by_extension`,
   `largest_files`, `list_files`).
3. `tests/test_files.py`: add tests that take the `sample_repo` fixture (rule 1):
   - Top-n on the sample repo: expected values computed from `SAMPLE_FILES` (`len(text.encode())`), not hard-coded,
     with `.git/config` excluded. Check `n=2` and the ordering.
   - Tie-breaking: write two extra files of equal size into `sample_repo` inside the test, and assert path order.
   - `n` larger than the file count returns all 5 files; `n=0` returns `[]`.
   - `.git` skipped: a large file under `.git/` never appears even with a big `n`.
4. `CHANGELOG.md`: under `## Unreleased` add `- Added `largest_files`.` (rule 3).
5. `README.md`: optionally add a one-line usage example next to the existing ones.

No dependencies change (rule 4); stdlib only.

## Testing
`ruff check .`, `ruff format --check .`, `pytest --doctest-modules` (the same three CI runs). The conventions test
confirms the doctest exists.

## Risks
- Symlinks: `list_files` uses `is_file()`, which follows symlinks, and `stat()` follows them too, so sizes are those of
  the target. This matches `list_files`; a file removed between listing and `stat` would raise `FileNotFoundError`
  (accepted, as in any race).
- `n < 0`: treated as `[]` rather than raising. Chosen for leniency; a `ValueError` is the alternative if the
  owner prefers strictness, but the goal doesn't ask for it.
- Tie test mutates the shared fixture directory only within that test (function-scoped `tmp_path`), so other tests are
  unaffected. Extending the fixture itself would require updating the `list_files` tests, so I avoid that.
- Reuses `list_files`, which sorts and walks everything; fine for repo-sized trees.

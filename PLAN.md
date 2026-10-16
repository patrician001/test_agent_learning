# Plan: add `largest_files(root, n=5)`

## Files
- repostats/files.py
- repostats/__init__.py
- tests/test_files.py
- CHANGELOG.md

## Changes
- `repostats/files.py`
  - Add `largest_files(root: str | Path, n: int = 5) -> list[tuple[str, int]]`.
  - Build `(path, (base / path).stat().st_size)` for each `path` in `list_files(root)`. That keeps `.git` skipped.
  - Sort with key `(-size, path)` so the largest comes first and ties break by path. Return the first `n`.
  - Behaviour for `n <= 0` is an empty list, which falls out of slicing with `max(n, 0)`. Using `[:n]` directly would be wrong for negative `n`.
  - Add a doctest in the style of `list_files`: tempdir, write files of known sizes including a tie, and show the output.
  - `ruff format --check` currently fails on this file because of `Counter( Path(p).suffix for p in list_files(root) )` in `count_by_extension`. Run `ruff format repostats/files.py` so CI goes green. It is whitespace only, and the file is already being edited.
- `repostats/__init__.py`: import `largest_files` and add it to `__all__`, keeping alphabetical order.
- `tests/test_files.py`
  - Add `test_largest_files(sample_repo)` using the fixture.
  - Assert the default call returns all five non-`.git` files with sizes, largest first. `src/app.py` is the largest. The `.git/config` file must not appear.
  - Assert `n=2` truncates the result.
  - Assert the tie-break by path. In the fixture, check whether any two files have equal size. If none do, extend `sample_repo` in `tests/conftest.py` or write an extra file into `sample_repo` inside the test. Writing into the fixture's `tmp_path` is allowed because it is still the fixture tree.
  - Compute the expected sizes with `len(text.encode())` or literal numbers, not with the function under test.
  - If extending the shared fixture is needed, add `tests/conftest.py` to Files. Prefer writing the extra file inside the test to avoid changing the other tests' expectations.
- `CHANGELOG.md`: under `## Unreleased` add `- Added `largest_files` ...` (one line, starts with "Added").

## Testing
- `pytest --doctest-modules`
- `ruff check .`
- `ruff format --check .`

## Risks
- Symlinks: `list_files` uses `is_file()`, which follows symlinks. `stat()` also follows them, so a broken symlink is already excluded. No extra handling is needed.
- A file deleted between listing and `stat` would raise. This is an acceptable race for a snapshot tool.
- Formatting `files.py` touches one unrelated line. It is whitespace only and needed for green CI.
- Stdlib only, and `pyproject.toml` is not touched.

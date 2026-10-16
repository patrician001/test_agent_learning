# Plan: add `largest_files(root, n=5)`

## Files
- repostats/files.py
- repostats/__init__.py
- tests/test_files.py
- CHANGELOG.md

## Changes

### repostats/files.py
- Add `largest_files(root: str | Path, n: int = 5) -> list[tuple[str, int]]`.
  - Build `(rel, (Path(root) / rel).stat().st_size)` for each `rel` in `list_files(root)`. That keeps `.git` skipped.
  - Sort with key `(-size, path)`: largest first, ties by path. Return the first `n` items.
  - `n <= 0` returns `[]`. Slice with `max(n, 0)` so a negative `n` doesn't slice from the end.
  - Standard library only. No new imports are needed.
- Docstring with a doctest in the style of the neighbouring functions. Use a temp dir with a few files of different sizes plus two files of equal size, and show the order and the tie-break. Include an `n` limit in the example.
- `ruff format --check .` currently fails on main because of `Counter( Path(p) ... )` in `count_by_extension` (commit 0851774). Since this file is already being edited, run `ruff format repostats/files.py` so CI goes green. Only that whitespace changes. If the reviewer wants that kept out of this PR, drop it. It is a one-line, behaviour-neutral change.

### repostats/__init__.py
- Import `largest_files` and add it to `__all__`, keeping the list sorted: `["count_by_extension", "largest_files", "list_files"]`.

### tests/test_files.py
- Add tests that take the `sample_repo` fixture. `conftest.py` stays unchanged.
- Sizes in `sample_repo` in bytes: `src/app.py` 51, `README.md` 30, `Makefile` 15, `docs/guide.md` 17, `src/util.py` 10. The implementer should re-verify these with `len(text.encode())`.
  - `test_largest_files`: `largest_files(sample_repo, 3)` equals `[("src/app.py", 51), ("README.md", 30), ("docs/guide.md", 17)]`.
  - The default `n=5` returns all 5 files, and `.git/config` is absent. This shows `.git` is skipped.
  - `n` larger than the file count returns every file. `n=0` returns `[]`.
  - Tie-break: write two same-size files into `sample_repo` inside the test, then assert path order. This reuses the fixture's tmp dir and builds no separate tree.

### CHANGELOG.md
- Under `## Unreleased`, add the line `- Added \`largest_files\` to list the n largest files under a directory.`

## Testing
- `pytest --doctest-modules`, `ruff check .`, `ruff format --check .`. All three should pass, including the format check that is currently red.

## Risks
- Symlinks: `list_files` uses `is_file()`, which follows symlinks. A broken symlink is not a file and is skipped. A file removed between listing and `stat` raises `FileNotFoundError`. That race is acceptable and is not handled.
- Negative `n` is handled as an empty result. The goal doesn't specify this, so it is a deliberate choice, documented in the tests.
- The formatting fix to the existing line in `files.py` is outside the strict goal but is needed for green CI.

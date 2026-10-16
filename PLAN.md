# Plan: `largest_files(root, n)`

## Files to change

1. `repostats/files.py`
   - Add `largest_files(root: str | Path, n: int) -> list[tuple[str, int]]`.
   - Build on `list_files(root)`, so the `.git` skipping and "/" separators match it. Pair each path with `(base / path).stat().st_size`.
   - Sort by `(-size, path)` and return the first `n`. That gives largest first, ties broken by path.
   - `n == 0` returns `[]`. A negative `n` raises `ValueError`, because a bare slice would silently return the wrong files.
   - Docstring with a passing `>>>` example, in the style of `list_files`. Create two files of different sizes in a temp dir and show the result. This satisfies CONTRIBUTING rule 2, which `tests/test_conventions.py` enforces.
2. `repostats/__init__.py`: import `largest_files` and add it to `__all__`, which stays sorted.
3. `tests/test_files.py`: new tests that take the `sample_repo` fixture (rule 1).
   - Ordering and sizes: with `n` larger than the file count, the result is every file except `.git/config`, ordered by size. Expected sizes are computed with `len(text.encode())` from `SAMPLE_FILES`, not hard-coded.
   - `n` limits the result: `largest_files(sample_repo, 2)` has length 2 and is the top two.
   - Tie-break by path: write two same-size files into `sample_repo` inside the test, then check that they come out in path order.
   - `.git` is skipped: `.git/config` never appears, even with a huge `n`. Write a large file under `.git` in the test to prove it.
   - `n=0` returns `[]`. A negative `n` raises `ValueError`.
4. `CHANGELOG.md`: under `## Unreleased`, add `- Added \`largest_files\`.` (rule 3).
5. `README.md`: optionally add a one-line usage example next to the `list_files` example. It is not required.

No change to `pyproject.toml`. There are no new dependencies (rule 4).

## Testing

Run `ruff check .`, `ruff format --check .` and `pytest --doctest-modules`. These are the same checks CI runs. The convention tests should pass without change.

## Risks

- **Tie and `.git` tests need extra files.** Extending the shared fixture would change the expected output of the existing `list_files` and `count_by_extension` tests. So those tests write their extra files into `sample_repo` themselves. If a reviewer reads rule 1 strictly, the alternative is to extend the fixture and update the existing tests, which makes the diff bigger.
- **Symlinks.** `list_files` counts symlinks to files (`is_file()` follows them). `stat()` follows them too, so the size is the target's size. A broken symlink is not a file, so it is skipped. This matches `list_files`, and the docstring should note it.
- **Race conditions.** A file deleted between listing and `stat` would raise `FileNotFoundError`. This is accepted, and no special handling is added.
- **Cost.** One `stat` per file, plus a full sort. This is fine for repository-sized trees.

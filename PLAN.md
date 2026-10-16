# Plan: add `find_todos(root)`

## Files to change

1. **`repostats/files.py`** – add `find_todos(root: str | Path) -> list[tuple[str, int, str]]`.
   - Iterate `list_files(root)`. It already skips `.git`, uses "/" separators and returns sorted paths, so ordering by path comes for free and the function matches `list_files`.
   - For each path, read bytes and `decode("utf-8")` strictly. On `UnicodeDecodeError`, skip the file.
   - Split with `text.split("\n")`, not `splitlines()`, so `\x0b`, `\x0c` and ` ` don't break lines and line numbers stay correct (the spirit of lesson L1). A trailing `\n` gives an empty last element, which never matches. Use `enumerate(..., 1)`.
   - A line matches if `re.search(r"\bTODO\b", line)`. The goal says "the word TODO", so `TODOS` and `MYTODO` don't match, but `TODO:` and `# TODO(bob)` do. Matching is case-sensitive. Add `import re` (stdlib).
   - Emit `(rel_path, lineno, line.strip())`. `strip()` also removes a trailing `\r` from CRLF files.
   - Results are already in path-then-line order because paths are sorted and lines are enumerated in order. Paths sort as `list_files` sorts them, by string.
   - The docstring has a doctest: a temp dir with one file containing a TODO line, showing the returned tuple. This satisfies CONTRIBUTING rule 2, which `tests/test_conventions.py` enforces.
2. **`repostats/__init__.py`** – import `find_todos` and add it to `__all__`, keeping the list sorted.
3. **`tests/test_files.py`** – new tests that use the `sample_repo` fixture (rule 1). Do not change the fixture. Adding files to it would break the existing `list_files` and `count_by_extension` assertions, so each test writes its extra files into `sample_repo` itself.
   - Baseline: `find_todos(sample_repo) == [("src/app.py", 2, "# TODO: handle errors")]`. The fixture's `.git/config` isn't scanned.
   - Whitespace is stripped, and line numbers start at 1 and count blank lines.
   - Ordering: add `a/z.txt` and `b.txt` with TODOs, plus a second TODO in one file. Assert the order is by path, then line.
   - Skips `.git`: write `.git/hooks/x` containing TODO and assert it is absent.
   - Skips invalid UTF-8: write `bin.dat` with `b"TODO \xff\xfe\n"` and assert it is absent.
   - Word boundary: `TODOS` and `todo` don't match.
   - Regression for the line-splitting concern: a file with `"a\x0cb\nTODO\n"` reports line 2. Also cover an empty file (no crash, no result) and a file whose last line has no trailing newline.
   - CRLF file: the result has no `\r`.
4. **`CHANGELOG.md`** – under `## Unreleased` add `- Added \`find_todos\`, which lists the lines containing TODO as (path, line number, text) tuples.` (rule 3).

No changes to `pyproject.toml` (rule 4: stdlib only).

## Testing

Run `ruff check .`, `ruff format --check .` and `pytest --doctest-modules` (what CI runs). The existing `test_every_public_function_has_a_doctest` covers the doctest rule.

## Risks

- **Matching semantics:** `\bTODO\b` is a judgement call on "the word TODO". A plain substring match would also catch `TODOS`. Easy to change in one line; the choice is noted in the docstring.
- **Unreadable files** (permission errors, broken symlinks that `is_file` already excludes): the plan lets `OSError` propagate rather than silently hiding it. The goal only asks to skip non-UTF-8 files.
- **Large files:** each file is read fully into memory. This is acceptable for a small stats package.
- **Sorting:** paths sort by string, so `a-b/x` sorts relative to `a/x` per `list_files`. This is consistent with the existing function.
- **UTF-8 BOM:** a leading BOM is not whitespace, so it stays on the first line's text. Minor; left as-is.

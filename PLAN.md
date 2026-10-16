# Plan: honour a root `.statsignore` in `list_files` / `count_by_extension`

## Background
`repostats/files.py` has `list_files(root)` (rglob, skips `.git`) and `count_by_extension(root)`, built on `list_files`,
so filtering inside `list_files` fixes both. CONTRIBUTING.md: tests use the `sample_repo` fixture, public functions have
doctests, CHANGELOG entry under `## Unreleased`, **no dependencies**. So no `pathspec`; `fnmatch` is not enough (`*`
crosses `/`, no anchoring or dir-only), so a small gitignore-style matcher is written by hand with `re`.

## Files to change

### `repostats/files.py`
Private helpers (underscore names, no doctest required; short doctests welcome):

- `_load_patterns(base)`: read `base / ".statsignore"` if it is a file (UTF-8, `errors="replace"`), else `[]`. Per line:
  strip `\n`/`\r`; drop trailing spaces that are **not** backslash-escaped (an escaped space `\ ` is kept, the backslash
  is handled by the compiler); skip blank lines and lines starting with `#`. Return compiled `(regex, negated,
  dir_only)` tuples.
- `_compile(line)`: a single left-to-right tokenizer that builds the regex. Defined syntax:
  1. Leading `!` → negated (then removed). Leading `\!` / `\#` → literal `!` / `#` (via rule 4). A line starting with
     an unescaped `#` was already skipped as a comment.
  2. Trailing unescaped `/` → directory-only (removed). A leading `/`, or a `/` anywhere else, anchors the pattern to the
     root; a pattern without `/` matches the basename at any depth (regex prefix `(?:.*/)?`).
  3. Wildcards: `*` = `[^/]*`; `?` = `[^/]`; `[...]` = character class (`!` or `^` after `[` negates, ranges allowed,
     never matches `/`; an unterminated `[` is a literal `[`). `**` forms, only when delimited by `/` or the pattern
     ends: leading `**/` = zero or more leading directories; trailing `/**` = everything inside; infix `/**/` = zero or
     more directories. Any other `**` behaves like `*`.
  4. **General backslash escaping:** `\` followed by any character `c` makes `c` a literal (`re.escape(c)`), so
     `literal\*.txt` matches the file `literal*.txt`, `\?`, `\[`, `\*`, `\\`, `\#`, `\!` and `\ ` (space) are literals,
     and an escaped space at the end of a line survives trailing-space stripping and matches a name ending in a
     space. A lone `\` at end of line is ignored (as in git, the pattern is invalid) rather than raising.
  5. Everything else is `re.escape`d; the regex is `fullmatch`ed against the relative POSIX path.
- `_is_ignored(rel_parts, is_dir, patterns)`: walk the ancestors from the top. If an ancestor directory is ignored
  (last matching pattern wins, negation un-ignores), the path is excluded and **no pattern can re-include it**
  (git semantics). Otherwise evaluate the path itself, last match wins.
- `list_files`: load patterns once; apply `_is_ignored` per file in addition to the `.git` check. `.statsignore` is not
  special-cased: listed unless a pattern matches it. Update docstring + doctest (a `.statsignore` containing `*.md`).
- `count_by_extension`: no code change; docstring mention only.
- Out of scope, documented in the docstring: nested `.statsignore`, `.gitignore`, global excludes; only `root`'s file.

### `tests/conftest.py`
Leave `SAMPLE_FILES` and `sample_repo` unchanged (existing expectations stay valid). Add fixture `statsignore`
(depends on `sample_repo`) returning a callable `(patterns, extra_files=()) -> Path` that writes the extra files
(creating parents) and `.statsignore` into the `sample_repo` tree and returns the root. Tests only call
`list_files(root)`, keeping them on `sample_repo` per rule 1.

### `tests/test_files.py`
All use `statsignore`; each asserts the exact `list_files` result (or the ignored set diff against the baseline).
Extra files are named per test. Tests are parametrized where convenient.

Basics:
- no `.statsignore` → output equals the existing baseline; empty file and a `.statsignore` *directory* → no crash,
  nothing ignored.
- `*.log` ignores root and nested logs; `build/` ignores the directory's contents but not a *file* named `build`;
  `docs/*.md` ignores `docs/guide.md` but not `README.md` or `docs/sub/x.md`; `/README.md` anchors vs. nested
  `src/README.md`; blank lines, `# comment`, trailing spaces and CRLF line endings are ignored.
- `.statsignore` is listed by default; disappears with `.statsignore` or `.*`; `.git` still skipped.
- `count_by_extension` reflects the filtered set.

**O1 – glob and ordering features, each its own test:**
- `**/` leading: `**/gen.py` matches `gen.py` (zero dirs), `a/gen.py` (one), `a/b/gen.py` (multiple); not `xgen.py`.
- `/**` trailing: `out/**` ignores `out/a`, `out/b/c` (any depth) but not `out` itself as a file name elsewhere
  (e.g. file `out` at root is unaffected only if it is a file: assert actual behaviour for an `out` directory
  containing files = all contents ignored).
- `/**/` infix: `a/**/z.txt` matches `a/z.txt` (zero), `a/b/z.txt` (one), `a/b/c/z.txt` (multiple); not `b/a/z.txt`
  (anchored) and not `a/z.txt.bak`.
- `?` matches exactly one non-`/` char: `f?.txt` matches `f1.txt`, not `f.txt`, `f12.txt`, or `f/x.txt` dir split.
- Character classes: `[ab].txt`, ranges `[0-9].dat`, negated `[!a].txt` and `[^a].txt`; class does not match `/`;
  unterminated `[` treated as a literal.
- Escaped leading `#` / `!`: `\#hash.txt` ignores file `#hash.txt` (and an unescaped `#hash.txt` line is a comment, so
  ignores nothing); `\!bang.txt` ignores file `!bang.txt` and is not a negation.
- Last-match ordering: `*.md` then `!README.md` re-includes README only; reversed order (`!README.md` then `*.md`)
  ignores it; three-pattern ignore / unignore / ignore sequence → ignored.
- Re-inclusion beneath an excluded parent: `build/` then `!build/keep.txt` (and `!build/**`) still ignores
  `build/keep.txt`; contrast with `build/*` then `!build/keep.txt`, where the parent is not excluded and `keep.txt` is
  listed.

**O2 – backslash escapes:**
- `literal\*.txt` ignores file `literal*.txt` and does not ignore `literalX.txt` / `literal.txt`; same for `\?`, `\[`.
- Escaped `\\` matches a name containing a backslash (skip on platforms that cannot create it; Linux CI is fine).
- Escaped trailing space: line `trail\ ` (backslash, space) ignores the file `"trail "` and not `trail`; an *unescaped*
  trailing space (`plain.txt `) is stripped and ignores `plain.txt`.
- Lone trailing backslash does not raise and ignores nothing extra.

### `CHANGELOG.md`
Under `## Unreleased`: `Added support for a root `.statsignore` file (gitignore-style patterns) in `list_files` and
`count_by_extension`.`

### `README.md`
Add a short note only if it already has a usage section describing `list_files` behaviour.

## Testing
`ruff check .`, `ruff format --check .`, `pytest --doctest-modules` (also runs `test_conventions.py`). As a
cross-check during development only (not committed), compare matcher results to `git check-ignore` on a scratch repo
for the cases above, to confirm the tests encode real gitignore behaviour.

## Risks
- **Hand-written gitignore semantics may deviate from git** (`**`, escapes, classes, negation under excluded dirs).
  Mitigation: documented subset, the explicit test list above, and the `git check-ignore` cross-check. Known
  deliberate divergence: POSIX classes like `[[:alpha:]]` are unsupported.
- **Behaviour change** for repos that already contain a `.statsignore`; noted in the changelog.
- **Performance**: `rglob` still walks ignored trees; ancestor checks add regex passes per path. Acceptable here;
  pruning via `os.walk` is a follow-up.
- Case-sensitive matching (git's Linux default).
- Test filenames with `*`, `?`, `\`, trailing space, `#`, `!` cannot be created on Windows; CI is Linux (check
  `ci.yml`), and the tests skip if file creation fails.

# Plan: `python -m repostats` command-line entry point

## Behaviour
- `python -m repostats ROOT` prints `list_files(ROOT)`, one relative path per line.
- `python -m repostats --counts ROOT` prints `count_by_extension(ROOT)` as JSON (`json.dumps`, one line, keys already sorted by the library).
- If ROOT is not a directory: message `repostats: not a directory: ROOT` on stderr, exit status 2, nothing on stdout.
- Argument parsing uses stdlib `argparse`. A missing ROOT or an unknown option is an argparse usage error, which already exits with 2.
- No new dependencies (CONTRIBUTING rule 4).

## Files to change
1. **`repostats/cli.py`** (new). Holds the logic so that it can be tested in-process.
   - `main(argv: list[str] | None = None) -> int` builds the parser (`root` positional, `--counts` flag).
   - It checks `Path(root).is_dir()`. If the check fails, it writes the error to `sys.stderr` and returns 2.
   - Otherwise it prints the output and returns 0.
   - `main` is public, so its docstring needs a passing `>>>` doctest (rule 2, enforced by `tests/test_conventions.py`). The doctest can use `tempfile` like the existing ones, or call `main(["/nonexistent-dir"])` and show the return value 2. Stderr output in a doctest is not captured, so prefer a `--counts` run on an empty temp dir, which prints `{}` and returns 0.
2. **`repostats/__main__.py`** (new). Contains `from repostats.cli import main`, then `if __name__ == "__main__": raise SystemExit(main())`. The guard matters because `pytest --doctest-modules` and `walk_packages` import this module, and it must not run `main` on import. It defines no public functions, so the doctest-convention test is unaffected.
3. **`tests/test_cli.py`** (new). Uses the `sample_repo` fixture (rule 1) and does not build its own trees.
   - `main([str(sample_repo)])` with `capsys`: stdout is the five expected paths, one per line, and `.git/config` is absent. The return value is 0.
   - `--counts`: `json.loads(stdout) == {"": 1, ".md": 2, ".py": 2}`.
   - Non-directory ROOT, both a missing path and a regular file (`sample_repo / "Makefile"`): returns 2, stdout is empty, stderr mentions the path.
   - One subprocess test, `subprocess.run([sys.executable, "-m", "repostats", ...])`, to prove the `-m` wiring and the real exit status 2. It runs with `cwd` set to the repo root, or relies on an installed package. Check which works in CI (`ci.yml`) before relying on it.
   - Missing ROOT: `pytest.raises(SystemExit)` with code 2.
4. **`CHANGELOG.md`**: under `## Unreleased` add `- Added a command-line entry point: \`python -m repostats [--counts] ROOT\`.` (rule 3).
5. **`README.md`**: add a short usage section, if the README has a natural place for it (it has no existing usage matches).

`repostats/__init__.py` and `files.py` are unchanged.

## Testing
- `pytest --doctest-modules`, `ruff check .` and `ruff format --check .`, the same three checks CI runs.
- Manual check: `python -m repostats .` and `python -m repostats --counts .`, then `python -m repostats /nope; echo $?` should print 2.

## Risks
- **Paths with non-UTF-8 or newline characters** in file names print oddly. This is acceptable for a line-per-path format, and I would not handle it here.
- **Empty directory** prints nothing for the listing and `{}` for counts. I would avoid printing a blank line for the empty listing (`print` per path, not `"\n".join`).
- **Subprocess test portability**: it depends on the working directory or on installation. I would keep it to one test, or drop it if CI runs without an install.
- **Symlinked directory as ROOT**: `is_dir()` follows symlinks, so it is accepted. This is fine.
- **Option-like ROOT** such as `-x` needs `--` to be passed. This is standard argparse behaviour, so I would leave it.

from pathlib import Path

import pytest

SAMPLE_FILES = {
    "README.md": "# sample\n\nA small repository.\n",
    "src/app.py": "def main():\n    # TODO: handle errors\n    return 0\n",
    "src/util.py": "VALUE = 1\n",
    "docs/guide.md": "Read the README.\n",
    "Makefile": "check:\n\tpytest\n",
    ".git/config": "[core]\n",
}


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    """A small checkout: Markdown, Python, a Makefile, and a .git directory that is always skipped."""
    for name, text in SAMPLE_FILES.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return tmp_path


@pytest.fixture
def statsignore(sample_repo: Path):
    """Return write(patterns, extra_files=()): add files and a .statsignore to sample_repo, return its root."""

    def write(patterns: str, extra_files=()) -> Path:
        for name in extra_files:
            path = sample_repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x\n")
        (sample_repo / ".statsignore").write_text(patterns)
        return sample_repo

    return write

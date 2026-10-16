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

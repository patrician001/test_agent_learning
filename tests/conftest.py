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
def todo_repo(sample_repo: Path) -> Path:
    """sample_repo plus files that exercise TODO search: ordering, stripping, edge cases."""
    files = {
        ".git/notes.txt": b"TODO\n",
        "docs/notes.md": b"TODO one\nmiddle\nTODO two\n",
        "docs/indented.md": b"    TODO: indented   \n",
        "docs/words.md": b"TODOS\nAUTODOC\ntodo\n",
        "docs/ff.txt": b"header\x0cTODO: fix\nsecond TODO\n",
        "docs/crlf.txt": b"a\r\nTODO: b\rTODO: c\r\n",
        "docs/binary.bin": b"TODO \xff\n",
    }
    for name, data in files.items():
        path = sample_repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return sample_repo

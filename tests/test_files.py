import pytest
from conftest import SAMPLE_FILES

from repostats import count_by_extension, largest_files, list_files


def test_list_files_skips_git(sample_repo):
    assert list_files(sample_repo) == [
        "Makefile",
        "README.md",
        "docs/guide.md",
        "src/app.py",
        "src/util.py",
    ]


def test_count_by_extension(sample_repo):
    assert count_by_extension(sample_repo) == {"": 1, ".md": 2, ".py": 2}


def _sizes(text_by_name):
    return {name: len(text.encode()) for name, text in text_by_name.items()}


def _expected_sizes():
    sizes = _sizes({k: v for k, v in SAMPLE_FILES.items() if k != ".git/config"})
    return sorted(sizes.items(), key=lambda item: (-item[1], item[0]))


def test_largest_files_orders_by_size(sample_repo):
    assert largest_files(sample_repo, 100) == _expected_sizes()


def test_largest_files_limits_to_n(sample_repo):
    assert largest_files(sample_repo, 2) == _expected_sizes()[:2]


def test_largest_files_breaks_ties_by_path(sample_repo):
    (sample_repo / "zzz.bin").write_bytes(b"x" * 1000)
    (sample_repo / "aaa.bin").write_bytes(b"y" * 1000)
    assert largest_files(sample_repo, 2) == [("aaa.bin", 1000), ("zzz.bin", 1000)]


def test_largest_files_skips_git(sample_repo):
    (sample_repo / ".git" / "huge").write_bytes(b"z" * 5000)
    paths = [path for path, _ in largest_files(sample_repo, 1000)]
    assert not any(p.startswith(".git/") for p in paths)


def test_largest_files_zero_and_negative(sample_repo):
    assert largest_files(sample_repo, 0) == []
    with pytest.raises(ValueError):
        largest_files(sample_repo, -1)

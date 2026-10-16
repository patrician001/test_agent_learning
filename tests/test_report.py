from pathlib import Path

from repostats import extension_report


def test_sample_report(sample_repo: Path) -> None:
    assert extension_report(sample_repo) == (
        "| Extension | Files |\n| --- | --- |\n| .md | 2 |\n| .py | 2 |\n| (none) | 1 |"
    )


def test_empty_tree(sample_repo: Path) -> None:
    (sample_repo / "empty").mkdir()
    assert extension_report(sample_repo / "empty") == "| Extension | Files |\n| --- | --- |"

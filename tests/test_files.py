from repostats import count_by_extension, list_files


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


def ignore(repo, text):
    (repo / ".statsignore").write_bytes(text.encode())


BASE = [".statsignore", "Makefile", "README.md", "docs/api.md", "docs/guide.md", "docs/sub/deep.md"]


def test_no_statsignore_lists_everything(sample_repo_with_ignore):
    (sample_repo_with_ignore / ".statsignore").unlink()
    assert "debug.log" in list_files(sample_repo_with_ignore)
    assert "src/trace.log" in list_files(sample_repo_with_ignore)


def test_glob_matches_at_any_depth(sample_repo_with_ignore):
    files = list_files(sample_repo_with_ignore)
    assert "debug.log" not in files and "src/trace.log" not in files
    assert ".statsignore" in files


def test_dir_pattern(sample_repo_with_ignore):
    ignore(sample_repo_with_ignore, "build/\n")
    files = list_files(sample_repo_with_ignore)
    assert not any("build/" in f for f in files)
    assert "debug.log" in files


def test_dir_pattern_does_not_match_file(sample_repo_with_ignore):
    (sample_repo_with_ignore / "src" / "build").rename(sample_repo_with_ignore / "src" / "b")
    (sample_repo_with_ignore / "build").joinpath("out.o").unlink()
    (sample_repo_with_ignore / "build").rmdir()
    (sample_repo_with_ignore / "build").write_text("file")
    ignore(sample_repo_with_ignore, "build/\n")
    assert "build" in list_files(sample_repo_with_ignore)


def test_path_pattern_is_anchored(sample_repo_with_ignore):
    ignore(sample_repo_with_ignore, "docs/*.md\n")
    files = list_files(sample_repo_with_ignore)
    assert "docs/api.md" not in files and "docs/guide.md" not in files
    assert "docs/sub/deep.md" in files and "README.md" in files


def test_leading_slash_anchors(sample_repo_with_ignore):
    ignore(sample_repo_with_ignore, "/README.md\n/app.py\n")
    files = list_files(sample_repo_with_ignore)
    assert "README.md" not in files and "src/app.py" in files


def test_blank_comments_and_trailing_whitespace(sample_repo_with_ignore):
    ignore(sample_repo_with_ignore, "# *.md\n\n   \n*.log   \n")
    files = list_files(sample_repo_with_ignore)
    assert "debug.log" not in files and "README.md" in files


def test_crlf(sample_repo_with_ignore):
    ignore(sample_repo_with_ignore, "*.log\r\nbuild/\r\n")
    files = list_files(sample_repo_with_ignore)
    assert "debug.log" not in files and "build/out.o" not in files


def test_empty_statsignore(sample_repo_with_ignore):
    ignore(sample_repo_with_ignore, "")
    assert "debug.log" in list_files(sample_repo_with_ignore)


def test_statsignore_can_hide_itself(sample_repo_with_ignore):
    ignore(sample_repo_with_ignore, ".statsignore\n")
    assert ".statsignore" not in list_files(sample_repo_with_ignore)


def test_negation_and_last_match_wins(sample_repo_with_ignore):
    ignore(sample_repo_with_ignore, "*.log\n!src/trace.log\n")
    files = list_files(sample_repo_with_ignore)
    assert "debug.log" not in files and "src/trace.log" in files


def test_negation_under_ignored_dir_stays_ignored(sample_repo_with_ignore):
    ignore(sample_repo_with_ignore, "build/\n!build/out.o\n")
    assert "build/out.o" not in list_files(sample_repo_with_ignore)


def test_double_star(sample_repo_with_ignore):
    ignore(sample_repo_with_ignore, "docs/**/*.md\n")
    files = list_files(sample_repo_with_ignore)
    assert "docs/api.md" not in files and "docs/sub/deep.md" not in files
    ignore(sample_repo_with_ignore, "**/trace.log\ndocs/**\n")
    files = list_files(sample_repo_with_ignore)
    assert "src/trace.log" not in files and not any(f.startswith("docs/") for f in files)


def test_escapes_and_classes(sample_repo_with_ignore):
    (sample_repo_with_ignore / "#x").write_text("")
    ignore(sample_repo_with_ignore, "\\#x\nsrc/[au]*.py\n")
    files = list_files(sample_repo_with_ignore)
    assert "#x" not in files and "src/app.py" not in files and "src/util.py" not in files


def test_count_by_extension_reflects_ignores(sample_repo_with_ignore):
    ignore(sample_repo_with_ignore, "*.log\n*.o\n*.md\n")
    assert count_by_extension(sample_repo_with_ignore) == {"": 2, ".py": 2}


def test_statsignore_directory_does_not_crash(sample_repo):
    (sample_repo / ".statsignore").mkdir()
    (sample_repo / ".statsignore" / "f").write_text("")
    assert ".statsignore/f" in list_files(sample_repo)


def test_nested_statsignore_ignored(sample_repo_with_ignore):
    (sample_repo_with_ignore / "docs" / ".statsignore").write_text("*.md\n")
    assert "docs/api.md" in list_files(sample_repo_with_ignore)

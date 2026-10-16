"""Small statistics about the files in a repository checkout."""

from repostats.files import count_by_extension, list_files
from repostats.lines import count_lines, lines_by_extension

__all__ = ["count_by_extension", "count_lines", "lines_by_extension", "list_files"]

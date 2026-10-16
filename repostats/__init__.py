"""Small statistics about the files in a repository checkout."""

from repostats.files import count_by_extension, list_files
from repostats.lines import count_lines

__all__ = ["count_by_extension", "count_lines", "list_files"]

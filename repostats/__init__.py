"""Small statistics about the files in a repository checkout."""

from repostats.files import count_by_extension, list_files
from repostats.report import extension_report

__all__ = ["count_by_extension", "extension_report", "list_files"]

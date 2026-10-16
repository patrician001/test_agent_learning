"""Small statistics about the files in a repository checkout."""

from repostats.files import count_by_extension, list_files
from repostats.remote import fetch_text

__all__ = ["count_by_extension", "fetch_text", "list_files"]

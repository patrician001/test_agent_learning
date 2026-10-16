"""Command-line entry point: ``python -m repostats [--counts] ROOT``."""

import argparse
import json
import sys
from pathlib import Path

from repostats.files import count_by_extension, list_files


def main(argv: list[str] | None = None) -> int:
    """Print the files under ROOT, or with --counts the per-extension counts as JSON.

    Returns the exit status: 0 on success, 2 if ROOT is not a directory.

    >>> import tempfile
    >>> main(["--counts", tempfile.mkdtemp()])
    {}
    0
    """
    parser = argparse.ArgumentParser(prog="repostats", description=__doc__)
    parser.add_argument("root", help="directory to inspect")
    parser.add_argument(
        "--counts", action="store_true", help="print file counts per extension as JSON"
    )
    args = parser.parse_args(argv)

    if not Path(args.root).is_dir():
        print(f"repostats: not a directory: {args.root}", file=sys.stderr)
        return 2
    if args.counts:
        print(json.dumps(count_by_extension(args.root)))
    else:
        for path in list_files(args.root):
            print(path)
    return 0

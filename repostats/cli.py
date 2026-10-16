"""Command-line interface: python -m repostats [--counts] ROOT."""

import argparse
import json
import sys
from pathlib import Path

from repostats.files import count_by_extension, list_files


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit status (2 if ROOT is not a directory).

    >>> main(["/nonexistent-repostats-root"])
    2
    """
    parser = argparse.ArgumentParser(
        prog="repostats", description="List or count the files under ROOT."
    )
    parser.add_argument("root", metavar="ROOT", help="directory to inspect")
    parser.add_argument(
        "--counts", action="store_true", help="print file counts by extension as JSON"
    )
    args = parser.parse_args(argv)

    if not Path(args.root).is_dir():
        print(f"repostats: error: not a directory: {args.root}", file=sys.stderr)
        return 2
    if args.counts:
        print(json.dumps(count_by_extension(args.root)))
    else:
        for path in list_files(args.root):
            print(path)
    return 0

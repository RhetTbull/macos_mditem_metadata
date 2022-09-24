"""Read metadata attributes from a file on macOS using MDItemCopyAttribute."""

import os
import sys

import CoreServices


def getmd(path: str, attr: str) -> str:
    """Return the value of the metadata attribute attr for the file at path."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    md = CoreServices.MDItemCreate(None, path)
    return CoreServices.MDItemCopyAttribute(md, attr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: getmd.py path attr")
        sys.exit(1)
    print(getmd(sys.argv[1], sys.argv[2]))

"""Copy NSURL Resource Key constants from https://developer.apple.com/documentation/foundation/nsurlresourcekey"""

# To use this:
# Open the URL above in a browser
# Run the script
# Click on every item in the "NSURLResourceKey" section
# Copy the text that looks like:
#   NSURLIsDirectoryKey
#   Key for determining whether the resource is a directory, returned as a Boolean NSNumber object (read-only).
#   iOS 4.0+ iPadOS 4.0+ macOS 10.6+ Mac Catalyst 13.1+ tvOS 9.0+ watchOS 2.0+ 
# This script will detect the text on clipboard and extract the data from the copied text.
# The script will then write the data to constants.json

import json
import re
import sys
import time
from typing import Dict

import pyperclip


def unidequote(s: str) -> str:
    """Replace unicode quotes from string with ascii quotes"""
    s = re.sub("\u201c", '"', s)
    s = re.sub("\u201d", '"', s)
    s = re.sub("\u2018", "'", s)
    s = re.sub("\u2019", "'", s)
    return s


def extract_data(buffer: str) -> Dict[str, str]:
    """Extract data from buffer. Buffer expected to be in format:

    NSURLIsDirectoryKey
    Key for determining whether the resource is a directory, returned as a Boolean NSNumber object (read-only).
    iOS 4.0+ iPadOS 4.0+ macOS 10.6+ Mac Catalyst 13.1+ tvOS 9.0+ watchOS 2.0+ 

    Some records don't have a description (2nd line)
    """
    lines = buffer.splitlines()
    if 1 < len(lines) > 3:
        return None

    # name
    if not lines[0].endswith("Key"):
        return None
    data = {"name": lines[0].strip()}

    data["description"] = unidequote(lines[1].strip()) if len(lines) == 3 else ""

    # line 3 is availability
    data["version"] = unidequote(lines[-1].strip())

    return data


def main():
    """Monitors clipboard for changes and extracts data from copied text"""
    data = []
    try:
        # clear clipboard
        pyperclip.copy("")
        last_buffer = ""
        while True:
            buffer = pyperclip.paste()
            if buffer == last_buffer:
                time.sleep(0.1)
                continue
            if data_item := extract_data(buffer):
                print(f"Extracted data: {data_item}")
                data.append(data_item)
            else:
                print(f"No data found in buffer:\n{buffer}", file=sys.stderr)
            last_buffer = buffer

    except KeyboardInterrupt:
        print("\nDone")

    open("constants.json", "w").write(json.dumps(data, indent=4))


if __name__ == "__main__":
    main()

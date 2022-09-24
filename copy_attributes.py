"""Copy constants from https://developer.apple.com/documentation/coreservices/file_metadata/mditem/common_metadata_attribute_keys?language=objc"""

# To use this:
# Open the URL above in a browser
# Run the script
# Click on every item in the "Common Metadata Attribute Keys" section
# Copy the text that looks like:
#   kMDItemAttributeChangeDate
#   The date and time of the last change made to a metadata attribute. A CFDate.
#   macOS 10.4+
# This script will detect the text on clipboard and extract the data from the copied text.
# The script will then write the data to constants.json

import json
import sys
import time
from typing import Dict
import re

import pyperclip


def unidequote(s: str) -> str:
    """Replace unicode quotes from string with ascii quotes"""
    s = re.sub("\u201c", '"', s)
    s = re.sub("\u201d", '"', s)
    return s


def extract_data(buffer: str) -> Dict[str, str]:
    """Extract data from buffer. Buffer expected to be in format:

    kMDItemAttributeChangeDate
    The date and time of the last change made to a metadata attribute. A CFDate.
    macOS 10.4+

    Some lines don't have a type.
    """
    lines = buffer.splitlines()
    if len(lines) != 3:
        return None

    # name
    if not lines[0].startswith("kMDItem"):
        return None
    data = {"name": lines[0].strip()}

    # description and type
    # would like to split on '. ' but some of the descriptions on Apple's site
    # don't include a space after the period
    descr_type = [l.strip() for l in lines[1].split(".")]
    if len(descr_type) < 2:
        return None
    if not descr_type[-1]:
        # remove empty string at end
        descr_type.pop()

    # some descriptions don't have a type
    if len(descr_type) == 1:
        descr_type.append("")  # no type

    # adding stripped period to end of description
    descr_type[-2] = f"{descr_type[-2]}."
    data["description"] = ". ".join(unidequote(d) for d in descr_type[:-1])

    data["type"] = descr_type[-1]
    # data type is in form 'A CFDate' or 'A CFString' or 'An CFArray of CFString'
    if data["type"].startswith("A "):
        data["type"] = data["type"][2:]
    elif data["type"].startswith("An "):
        data["type"] = data["type"][3:]
    elif not data["type"]:
        data["type"] = None

    # macOS version
    data["version"] = lines[2].strip()

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

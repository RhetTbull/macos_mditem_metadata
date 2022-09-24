"""Set metadata on macOS files using undocumented function MDItemSetAttribute

Background: Apple provides MDItemCopyAttribute to get metadata from files:
https://developer.apple.com/documentation/coreservices/1427080-mditemcopyattribute?language=objc

but does not provide a documented way to set file metadata.

This script shows how to use the undocumented function MDItemSetAttribute to do so.

`pip install pyobjc` to install the required Python<-->Objective C bridge package.
"""

import datetime
import os
import sys
from typing import List, Union

import CoreFoundation
import CoreServices
import objc

# Absolute time in macOS is measured in seconds relative to the absolute reference date of Jan 1 2001 00:00:00 GMT.
# Reference: https://developer.apple.com/documentation/corefoundation/1542812-cfdategetabsolutetime?language=objc
MACOS_TIME_DELTA = (
    datetime.datetime(2001, 1, 1, 0, 0) - datetime.datetime(1970, 1, 1, 0, 0)
).total_seconds()

# load undocumented function MDItemSetAttribute
# signature: Boolean MDItemSetAttribute(MDItemRef, CFStringRef name, CFTypeRef attr);
# references:
# https://github.com/WebKit/WebKit/blob/5b8ad34f804c64c944ebe43c02aba88482c2afa8/Source/WTF/wtf/mac/FileSystemMac.MDItemSetAttribute
# https://pyobjc.readthedocs.io/en/latest/metadata/manual.html#objc.loadBundleFunctions
# signature of B@@@ translates to returns BOOL, takes 3 arguments, all objects
# In reality, the function takes references (pointers) to the objects, but pyobjc barfs if
# the function signature is specified using pointers.
# Specifying generic objects allows the bridge to convert the Python objects to the
# appropriate Objective C object pointers.


def MDItemSetAttribute(mditem, name, attr):
    """dummy function definition"""
    ...


# This will load MDItemSetAttribute from the CoreServices framework into module globals
objc.loadBundleFunctions(
    CoreServices.__bundle__,
    globals(),
    [("MDItemSetAttribute", b"B@@@")],
)


def set_file_metadata(
    file: str, attribute: str, value: Union[str, List, datetime.datetime]
) -> bool:
    """Set file metadata using undocumented function MDItemSetAttribute

    file: path to file
    attribute: metadata attribute to set
    value: value to set attribute to; must match the type expected by the attribute (e.g. str or list)

    Note: date attributes (e.g. kMDItemContentCreationDate) not yet handled.

    Returns True if successful, False otherwise.
    """
    if not os.path.exists(file):
        raise FileNotFoundError(f"File not found: {file}")
    mditem = CoreServices.MDItemCreate(None, file)
    if isinstance(value, list):
        value = CoreFoundation.CFArrayCreate(
            None, value, len(value), CoreFoundation.kCFTypeArrayCallBacks
        )
    elif isinstance(value, datetime.datetime):
        value = CoreFoundation.CFDateCreate(None, value.timestamp() - MACOS_TIME_DELTA)
    return MDItemSetAttribute(
        mditem,
        attribute,
        value,
    )


def value_to_boolean(value: str) -> bool:
    """Convert string to boolean"""
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    elif value.isdigit():
        return bool(int(value))
    else:
        raise ValueError(f"Invalid boolean value: {value}")


def main():
    """Set metadata on macOS files using undocumented function MDItemSetAttribute

    Usage: setmd.py <file> <attribute> <type> <value> <value> ...

    <file>: path to file
    <attribute>: metadata attribute to set, e.g. kMDItemWhereFroms
    <type>: type of value to set, e.g. string or array; must match the type expected by the attribute (e.g. string, array, date, number, boolean)
    <value>: value(s) to set attribute to

    For example: setmd.py /tmp/test.txt kMDItemWhereFroms array http://example.com

    For metadata attributes and types, see https://developer.apple.com/documentation/coreservices/file_metadata/mditem/common_metadata_attribute_keys?language=objc

    types map to the following Objective C types:

    - string: CFString

    - array: CFArray of CFString

    - date: CFDate

    - number: CFNumber

    - boolean: CFBoolean

    date types must be in ISO 8601 format, e.g. '2021-01-01T00:00:00Z', '2021-01-01T00:00:00+00:00', '2021-01-01'
    boolean types must be 'true' or 'false' or '0' or '1'
    """
    # super simple argument parsing just for demo purposes
    if len(sys.argv) < 5:
        print(main.__doc__)
        sys.exit(1)

    file = sys.argv[1]
    attribute = sys.argv[2]
    type_ = sys.argv[3]
    values = sys.argv[4:]

    if type_ == "string":
        values = values[0]
    elif type_ == "date":
        values = values[0]
        values = datetime.datetime.fromisoformat(values)
    elif type_ == "number":
        values = values[0]
        values = float(values)
    elif type_ == "boolean":
        values = values[0]
        values = value_to_boolean(values)

    try:
        attribute = getattr(CoreServices, attribute)
    except AttributeError:
        print(f"Invalid attribute: {attribute}")
        sys.exit(1)

    if not set_file_metadata(file, attribute, values):
        print(f"Failed to set metadata attribute {attribute} on {file}")
        sys.exit(1)
    else:
        print(f"Successfully set metadata attribute {attribute} on {file} to {values}")


if __name__ == "__main__":
    main()

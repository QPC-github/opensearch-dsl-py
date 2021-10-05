# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.
#
# Modifications Copyright OpenSearch Contributors. See
# GitHub history for details.

"""Script which verifies that all source files have a license header.
Has two modes: 'fix' and 'check'. 'fix' fixes problems, 'check' will
error out if 'fix' would have changed the file.
"""

import os
import sys
from itertools import chain
from typing import Iterator, List

lines_to_keep = ["# -*- coding: utf-8 -*-\n", "#!/usr/bin/env python\n"]
license_header_lines = [
    "# SPDX-License-Identifier: Apache-2.0\n",
    "#\n",
    "# The OpenSearch Contributors require contributions made to\n",
    "# this file be licensed under the Apache-2.0 license or a\n",
    "# compatible open source license.\n",
    "#\n",
    "# Modifications Copyright OpenSearch Contributors. See\n",
    "# GitHub history for details.\n",
    "\n",
]


def find_files_to_fix(sources: List[str]) -> Iterator[str]:
    """Iterates over all files and dirs in 'sources' and returns
    only the filepaths that need fixing.
    """
    for source in sources:
        if os.path.isfile(source) and does_file_need_fix(source):
            yield source
        elif os.path.isdir(source):
            for root, _, filenames in os.walk(source):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    if does_file_need_fix(filepath):
                        yield filepath


def does_file_need_fix(filepath: str) -> bool:
    if not filepath.endswith(".py"):
        return False
    with open(filepath, mode="r") as f:
        first_license_line = None
        for line in f:
            if line == license_header_lines[0]:
                first_license_line = line
                break
            elif line not in lines_to_keep:
                return True
        for header_line, line in zip(
            license_header_lines, chain((first_license_line,), f)
        ):
            if line != header_line:
                return True
    return False


def add_header_to_file(filepath: str) -> None:
    with open(filepath, mode="r") as f:
        lines = list(f)
    i = 0
    for i, line in enumerate(lines):
        if line not in lines_to_keep:
            break
    lines = lines[:i] + license_header_lines + lines[i:]
    with open(filepath, mode="w") as f:
        f.truncate()
        f.write("".join(lines))
    print(f"Fixed {os.path.relpath(filepath, os.getcwd())}")


def main():
    mode = sys.argv[1]
    assert mode in ("fix", "check")
    sources = [os.path.abspath(x) for x in sys.argv[2:]]
    files_to_fix = find_files_to_fix(sources)

    if mode == "fix":
        for filepath in files_to_fix:
            add_header_to_file(filepath)
    else:
        no_license_headers = list(files_to_fix)
        if no_license_headers:
            print("No license header found in:")
            cwd = os.getcwd()
            [
                print(f" - {os.path.relpath(filepath, cwd)}")
                for filepath in no_license_headers
            ]
            sys.exit(1)
        else:
            print("All files had license header")


if __name__ == "__main__":
    main()

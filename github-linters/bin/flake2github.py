#!/usr/bin/env python3
"""
Convert flake8 output to GitHub Actions annotations.
Reads flake8 output from stdin and writes GitHub Actions annotations to stdout.
"""
import sys
import re

# flake8 output format:
# path/to/file.py:LINE:COLUMN: CODE MESSAGE
FLAKE8_PATTERN = re.compile(
    r"(?P<file>.*?):(?P<line>\d+):(?P<col>\d+):\s(?P<code>\w\d+)\s(?P<msg>.+)"
)


def main() -> int:
    """
    Entry point function.
    """
    had_errors = False

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue

        match = FLAKE8_PATTERN.match(line)
        if not match:
            # Если формат неизвестен — просто пробросим строку в лог
            print(line)
            continue

        data = match.groupdict()

        file = data["file"]
        line_no = data["line"]
        col_no = data["col"]
        code = data["code"]
        message = data["msg"]

        # Все сообщения flake8 считаем warning
        # (при желании можно поменять логику)
        level = "warning"

        # Escape special characters for GitHub Actions
        for old, new in [("%", "%25"), ("\n", "%0A"), ("\r", "%0D")]:
            message = message.replace(old, new)

        print(
            f"::{level} "
            f"file={file},"
            f"line={line_no},"
            f"col={col_no}::"
            f"{code} {message}"
        )

        had_errors = True

    return 1 if had_errors else 0


if __name__ == "__main__":
    sys.exit(main())

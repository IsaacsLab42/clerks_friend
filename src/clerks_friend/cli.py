import os
import sys
from argparse import ArgumentParser
from contextlib import contextmanager
from getpass import getpass
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Generator, TextIO

import arrow
from dotenv import load_dotenv
from lcr_session import LcrSession
from yaml import load

from . import reports
from .utils import dataclass_list_to_table

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


_DESCRIPTION = """Run clerk reports from LCR for The Church of Jesus Christ of Latter-Day
Saints.
"""


def value_or_env(
    value: str | None, env_var: str, prompt: str, hidden: bool = False
) -> str:
    """
    Get a value from the input `value` parameter, environment variable, or user prompt.

    Args:
        value: value from command line options
        env_var: name of the environment variable containing the value
        prompt: prompt to show the user if no other valid value is found
        hidden: whether the input should be hidden or not (for example, a password)

    Raises:
        ValueError: When the value is None or a 0 length string

    Returns:
        The value from the input, environment, or user.
    """
    if value is None:
        value = os.getenv(env_var)
        if value is None or len(value) == 0:
            if hidden:
                value = getpass(prompt)
            else:
                value = input(prompt)

    if len(value) == 0:
        raise ValueError("Input cannot be an empty string")

    return value


@contextmanager
def smart_open(filename: str | None = None) -> Generator[TextIO, None, None]:
    """
    Open the specified file, or stdout, for writing.

    Args:
        filename: File to open for write, or the special value '-' or None to write to
            the console (stdout).

    Yields:
        File object opened for writing.
    """
    if filename is not None and filename != "-":
        fp = open(filename, "wt")
    else:
        fp = sys.stdout

    try:
        yield fp
    finally:
        if fp is not sys.stdout:
            fp.close()


def run_reports() -> int:
    parser = ArgumentParser(description=_DESCRIPTION)
    parser.add_argument(
        "input",
        metavar="INPUT_FILE",
        type=Path,
        help="input YAML file containing the report configuration",
    )
    parser.add_argument(
        "-u",
        "--username",
        metavar="USERNAME",
        help="LCR username [env var: LCR_USERNAME]",
    )
    parser.add_argument(
        "-p",
        "--password",
        metavar="PASSWORD",
        help="LCR password [env var: LCR_PASSWORD]",
    )
    parser.add_argument(
        "-c",
        "--cookie-file",
        metavar="COOKIE_FILE",
        type=Path,
        help="cookie jar file to save the session or load a saved session",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="MARKDOWN_OUTPUT",
        type=Path,
        help="output file for markdown report. Defaults to stdout.",
    )

    args = parser.parse_args()

    load_dotenv()

    username = value_or_env(args.username, "LCR_USERNAME", "LCR Username: ")
    password = value_or_env(args.password, "LCR_PASSWORD", "LCR Password: ", True)

    input_file: Path = args.input
    with input_file.open("rt") as fp:
        yml_data = load(fp, Loader=Loader)

    lcr = LcrSession(username, password, cookie_jar_file=args.cookie_file)
    now = arrow.now()
    now_str = now.format("YYYY-MM-DD")
    with smart_open(args.output) as fp:
        fp.write("# " + yml_data["title"] + "\n")
        fp.write(f"Report run on: {now_str}\n")
        fp.write("\n")
        for report in yml_data["reports"]:
            fn_name = "get_" + report["name"]
            fn = getattr(reports, fn_name)
            fn_args = report.get("parameters", {})
            data = fn(lcr, **fn_args)
            markdown_data = dataclass_list_to_table(data)
            fp.write("## " + report["heading"] + "\n")
            fp.write(f"{markdown_data}\n")
            fp.write("\n")

    return 0

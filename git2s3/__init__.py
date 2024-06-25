"""Placeholder for packaging."""

import sys

from git2s3.main import Git2S3

version = "0.0.0-a"


def commandline() -> None:
    """Command-line entrypoint."""
    assert sys.argv[0].endswith("git2s3"), "Invalid commandline trigger!!"
    options = {
        "start | run": "Initiates Git2S3 process.",
        "version | -v | --version | -V": "Prints the version.",
        "help | --help": "Prints the help section.",
    }
    # weird way to increase spacing to keep all values monotonic
    _longest_key = len(max(options.keys()))
    _pretext = "\n\t* "
    choices = _pretext + _pretext.join(
        f"{k} {'·' * (_longest_key - len(k) + 8)}→ {v}".expandtabs()
        for k, v in options.items()
    )
    try:
        arg = sys.argv[1].lower()
    except (IndexError, AttributeError):
        print(
            f"Cannot proceed without arbitrary commands. Please choose from {choices}"
        )
        exit(1)

    match arg:
        case "start" | "run":
            Git2S3().start()
        case "version" | "-v" | "-V" | "--version":
            print(f"Git2S3 {version}")
        case "help" | "--help":
            print(
                f"Usage: git2s3 [arbitrary-command]\nOptions (and corresponding behavior):{choices}"
            )
        case _:
            print(f"Unknown Option: {arg}\nArbitrary commands must be one of {choices}")

"""Placeholder for packaging."""

import sys

import click

from git2s3.main import Git2S3

version = "0.1.0"


@click.command()
@click.argument("start", required=False)
@click.argument("run", required=False)
@click.option("--version", "-V", is_flag=True, help="Prints the version.")
@click.option("--help", "-H", is_flag=True, help="Prints the help section.")
@click.option(
    "--env",
    "-E",
    type=click.Path(exists=True),
    help="Environment configuration filepath.",
)
def commandline(*args, **kwargs) -> None:
    """Starter function to invoke Git2S3 via CLI commands.

    **Flags**
        - ``--version | -V``: Prints the version.
        - ``--help | -H``: Prints the help section.
        - ``--env | -E``: Environment configuration filepath.

    **Commands**
        ``start | run``: Initiates the backup process.
    """
    assert sys.argv[0].endswith("git2s3"), "Invalid commandline trigger!!"
    options = {
        "--version | -V": "Prints the version.",
        "--help | -H": "Prints the help section.",
        "--env | -E": "Environment configuration filepath.",
        "start | run": "Initiates the backup process.",
    }
    # weird way to increase spacing to keep all values monotonic
    _longest_key = len(max(options.keys()))
    _pretext = "\n\t* "
    choices = _pretext + _pretext.join(
        f"{k} {'·' * (_longest_key - len(k) + 8)}→ {v}".expandtabs()
        for k, v in options.items()
    )
    if kwargs.get("version"):
        click.echo(f"Git2S3 {version}")
        sys.exit(0)
    if kwargs.get("help"):
        click.echo(
            f"\nUsage: git2s3 [arbitrary-command]\nOptions (and corresponding behavior):{choices}"
        )
        sys.exit(0)
    trigger = kwargs.get("start") or kwargs.get("run")
    if trigger and trigger.lower() in ("start", "run"):
        Git2S3(env_file=kwargs.get("env") or ".env").start()
        sys.exit(0)
    elif trigger:
        click.secho(f"\n{trigger!r} - Invalid command", fg="red")
    else:
        click.secho("\nNo command provided", fg="red")
    click.echo(
        f"Usage: git2s3 [arbitrary-command]\nOptions (and corresponding behavior):{choices}"
    )
    sys.exit(1)

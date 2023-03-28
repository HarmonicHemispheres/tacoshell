"""
Copyright <<year>> <<insert publisher name>>
DESCRIPTION:
    this is a sample Typer CLI layout
USAGE EXAMPLE:
    > python template_simple_cli.py example_cmd
"""


# ::IMPORTS ------------------------------------------------------------------------ #

# cli framework - https://pypi.org/project/typer/
import typer

# data types for validation - https://docs.python.org/3/library/typing.html
from typing import Optional

# cross platform path handling - https://docs.python.org/3/library/pathlib.html
from pathlib import Path

# package for reading details about this package
# import pkg_resources
from pathlib import Path
from tacoshell.shell.shell import Shell

# ::SETUP -------------------------------------------------------------------------- #
app = typer.Typer(
    add_completion=False,
    invoke_without_command=True
    )

# ::CORE LOGIC --------------------------------------------------------------------- #
# place core script logic here and call functions
# from the cli command functions to separate CLI from business logic

# ::CLI ---------------------------------------------------------------------------- #

@app.callback(invoke_without_command=True)
def run(
    debug: bool = False,
    cfg: Path = Path("taco.toml")
):

    if not cfg.exists():
        cfg = None

    shell = Shell(cfg=cfg)
    shell.start()



# ::EXECUTE ------------------------------------------------------------------------ #
def main():
    app()


if __name__ == "__main__":  # ensure importing the script will not execute
    main()
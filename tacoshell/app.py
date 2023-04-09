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

# color and prompts for cli
from rich.panel import Panel
from rich.prompt import Prompt
from rich.prompt import Confirm
from rich.console import Console
from rich.table import Table
from rich import print

# package for reading details about this package
# import pkg_resources
from pathlib import Path
from tacoshell.core.shell import Shell
from tacoshell.config import load_config, Config, save_config
from tacoshell.core.ai import AiEngine

# ::SETUP -------------------------------------------------------------------------- #
app = typer.Typer(
    add_completion=False,
    no_args_is_help=True
    )

# ::CORE LOGIC --------------------------------------------------------------------- #
# place core script logic here and call functions
# from the cli command functions to separate CLI from business logic

# ::CLI ---------------------------------------------------------------------------- #

@app.command()
def chat(
    debug: bool = False,
    cfg: Path = Path("taco.toml")
):

    if not cfg.exists():
        cfg = None

    shell = Shell(cfg=cfg)
    shell.start()

@app.command()
def init():
    CON = Console()
    cfg_path = Path("taco.toml")
    cfg = None

    try:
        # -- LOOK FOR EXISTING CONFIG
        if cfg_path.exists():
            cfg = load_config(cfg_path)
        else:
            cfg = Config()

        # -- GET CONFIG
        config_path = Path(Prompt.ask(
            "Create a new taco config here?", 
            default=str(cfg_path)
            ))
        
        # -- GET OPENAI KEY
        openai_key = Prompt.ask("Your OpenAi Key?", default=cfg.openai_key)

        # -- GET DEFAULT CHAT MODEL
        if openai_key:
            ai = AiEngine(openai_key=openai_key)
            models, table = ai.get_chat_models()
            print(table)
            openai_chat_model = Prompt.ask("Choose a default Chat Model?", 
                                    default=cfg.openai_chat_model)


        # -- CONFRM SAVE
        cfg = Config(openai_key=openai_key, 
                     openai_chat_model=openai_chat_model)
        print(Panel(f"CONFIG READY TO CREATE! @ [blue]{config_path.absolute()}\n[red]{cfg.json(indent=3)}"))
        create_file: bool = Confirm.ask("Confirm Config Creation?")

        if create_file:
            save_config(cfg, config_path)
            print(f"[green]Config Created! Now run `taco chat` to start cookin up ideas!")

    except Exception as error:
        CON.print(f"ERROR:  {error}")
    
    # if not cfg.exists():
    #     cfg = None
    





# ::EXECUTE ------------------------------------------------------------------------ #
def main():
    app()


if __name__ == "__main__":  # ensure importing the script will not execute
    main()
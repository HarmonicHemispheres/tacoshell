# Tacoshell imports
from .ai import AiEngine
from tacoshell.config import load_config, Config
from tacoshell.core.context_manager import ContextManager, Entry, Csv
from tacoshell.core.db import Database, MODELS, MChatSessions

# color and prompts for cli
from rich.panel import Panel
from rich.console import Console

# other imports
from pathlib import Path
import subprocess
import sys

CON = Console()
CMD_TEXT = """
.quit   --  exit taco shell
.help   --  list builtin commands
.cfg   --  show the config settings
<TEXT>  --  ask openai a question
"""

class Shell:

    def __init__(self, cfg:Path = None):

        try:
            self.cfg_path = cfg
            self.cfg: Config = load_config(self.cfg_path)

            self.ai_engine = AiEngine(openai_key=self.cfg.openai_key,
                                      model=self.cfg.openai_chat_model)
            self.context = ContextManager()
            try:
                self.db = Database(create_new=True)
                self.db.create_chat_session(
                    MChatSessions(
                        session_id=self.db.gen_guid(),
                        name="first session!"
                    )
                )
                CON.print(self.db.list_tables())
                self.db.select_table("chat_sessions")

            except Exception as error:
                import traceback
                traceback.print_exc()

        except Exception as error:
            CON.print(f"ERROR setting up shell!\n -> {error}")



    def start(self):
        while True:
            try:
                # -- get command
                cmd = input("🌮 ")

                # -- PROCESS COMMAND
                resp = ""
                with CON.status("....Consulting Oracle"):
                    if cmd.startswith(".quit"):
                        break
                    elif cmd.startswith(".help"):
                        CON.print(CMD_TEXT)
                    elif cmd.startswith(".cfg"):
                        CON.print(Panel(f"CONFIG @ [blue]{self.cfg_path.absolute()}\n[red]{self.cfg.json(indent=3)}"))
                    else:
                        resp = self.ai_engine.get_resp(cmd)

                # -- show response
                if resp:
                    CON.print(f"🤖  {resp}\n")

            except Exception as error:
                CON.print(error)

        
        print("Wrapping Up Extra Tacos!")
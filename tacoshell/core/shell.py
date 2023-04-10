# Tacoshell imports
from .ai import AiEngine
from tacoshell.config import load_config, Config
from tacoshell.core.context_manager import ContextManager, Entry, Csv
from tacoshell.core.db import Database, MODELS, MChatSessions, MChatContent

# color and prompts for cli
from rich.panel import Panel
from rich.console import Console

# other imports
import pkg_resources
from pathlib import Path
from datetime import datetime
import subprocess
import sys

CON = Console()
CMD_TEXT = """
<TEXT>               --  ask openai a question

.quit                --  exit taco shell
.help                --  list builtin commands
.clear               --  clears the console
.clr                 --  clears the console
.cfg                 --  show the config settings
.session             --  show the details of the current session and its history
.sessions            --  list chat sessions
.ai-models           --  shows available OpenAi models
.set-session=<NAME>  --  switch to a different chat session
.set-s=<NAME>        --  switch to a different chat session
"""

class Shell:

    @property
    def taco_version(self):
        version = pkg_resources.get_distribution("tacoshell").version
        return version

    def __init__(self, cfg:Path = None, new_db: bool = False):

        try:
            self.cfg_path = cfg
            self.cfg: Config = load_config(self.cfg_path)

            self.ai_engine = AiEngine(openai_key=self.cfg.openai_key,
                                      model=self.cfg.openai_chat_model)
            self.context = ContextManager()

            self.active_session: MChatSessions = None

            try:
                self.db = Database(create_new=new_db)
                
                session = self.db.get_active_session()
                if session and isinstance(session, MChatSessions):
                    # -- LOAD EXISTING ACTIVE SESSION
                    self.active_session = session
                else:
                    # -- CREATE NEW SESSION
                    new_session = MChatSessions(
                            session_id=self.db.gen_guid(),
                            name="DEFAULT",
                            is_active=True
                        )
                    self.active_session = new_session
                    self.db.create_chat_session(new_session)

            except Exception as error:
                import traceback
                traceback.print_exc()

        except Exception as error:
            CON.print(f"ERROR setting up shell!\n -> {error}")



    def start(self, show_welcome=True):
        # messages = [{"role": "system", "content": "You are a helpful assistant."}]
        if show_welcome:
            version_str = self.taco_version
            current_time_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            filler_str = " "*(43 - (len(version_str)+len(current_time_str)+7))   # 43 total chars in row
            detail_row = f"┃ v{version_str} {filler_str} {current_time_str} ┃"
            banner = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ┏━━━━┓━━━┓━━━┓━━━┓┏━━━┓┓ ┏┓━━━┓┓ ┏━┓    ┃
┃ ┃┏┓┏┓┃┏━┓┃┏━┓┃┏━┓┃┃┏━┓┃┃┃┃┃┏━━┛┃┃┃┃┃┃┃┃ ┃
┃ ┗┛┃┃┗┛┃┃┃┃┃┃┗┛┃┃┃┃┃┗━━┓┗━┛┃┗━━┓┃┃┃┃┃┃┃┃ ┃
┃ ┃┃┃┃┃┃┗━┛┃┃┃┏┓┃┃┃┃┃━━┓┃┏━┓┃┏━━┛┃┃┏┓┃┃┏┓ ┃
┃ ┃┏┛┗┓┃┏━┓┃┗━┛┃┗━┛┃┓┗━┛┃┃┃┃┃┗━━┓┗━┛┃┗━┛┃ ┃
┃ ┃┗━━┛┃┛┃┗┛━━━┛━━━┛┛━━━┛┛┃┗┛━━━┛━━━┛━━━┛ ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
{detail_row}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


            """

            CON.print(banner)

        while True:
            # -- get command
            cmd = input("🌮 ")

            # -- get session messages
            messages = self.db.select_session_content(self.active_session.session_id)
            with CON.status(f"....Consulting {self.cfg.openai_chat_model}"):
                try:
                    if cmd.startswith(".quit"):
                        break
                    
                    elif cmd.startswith(".help"):
                        CON.print(CMD_TEXT)
                    
                    elif cmd.startswith(".cfg"):
                        CON.print(Panel(f"CONFIG @ [blue]{self.cfg_path.absolute()}\n[red]{self.cfg.json(indent=3)}"))
                    
                    elif cmd.startswith((".clear", ".clr")):
                        CON.clear()
                    
                    elif cmd.startswith(".sessions"):
                        self.db.select_table("chat_sessions")
                    
                    elif cmd.startswith(".ai-models"):
                        models, table = self.ai_engine.get_chat_models()
                        CON.print(table)
                    
                    elif cmd.startswith((".session",)):
                        # CON.print(f"SESSION:  [blue]{self.active_session.name}  [white]([green]{self.active_session.session_id}[white])")
                        # self.db.select_table("chat_content", where=f"session_ref = '{self.active_session.session_id}'")
                        self.db.show_session_content(self.active_session.session_id, self.active_session.name)

                    elif cmd.startswith((".set-session", ".set-s")):
                        session_name: str = cmd.split("=",maxsplit=1)[1]
                        session_name = session_name.strip()
                        session = self.db.set_active_session(session_name=session_name)
                        self.active_session = session
                        
                    else:
                        messages = self.ai_engine.get_resp(cmd, messages=messages)
                        self.db.create_chat_content(
                            MChatContent(
                                message_id=self.db.gen_guid(),
                                session_ref=self.active_session.session_id,
                                role=messages[-2].get("role"),
                                content=messages[-2].get("content"),
                                created=datetime.now()
                            )
                        )
                        self.db.create_chat_content(
                            MChatContent(
                                message_id=self.db.gen_guid(),
                                session_ref=self.active_session.session_id,
                                role=messages[-1].get("role"),
                                content=messages[-1].get("content"),
                                created=datetime.now()
                            )
                        )

                        # -- show response
                        if len(messages) > 0:
                            CON.print(f"🤖  {messages[-1].get('content')}\n")

                except Exception as error:
                    import traceback
                    traceback.print_exc()
                    # CON.print(error)

        
        print("Wrapping Up Extra Tacos!")
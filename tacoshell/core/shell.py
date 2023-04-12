# Tacoshell imports
from .ai import AiEngine
from tacoshell.config import load_config, Config
from tacoshell.core.context_manager import ContextManager, Entry, Csv
from tacoshell.core.db import Database, MChatSessions, MChatContent

# color and prompts for cli
from rich.panel import Panel
from rich.console import Console


# other imports
import pkg_resources
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import os


CON = Console()
CMD_TEXT = """
<TEXT>               --  ask openai a question in the current chat session

.quit                --  exit taco shell
.help                --  list builtin commands
.clear/.clr          --  clears the console
.cfg                 --  show the config settings
.session             --  show the details of the current session and its history
.sessions            --  list chat sessions
.models              --  shows available OpenAi models
.set-session <NAME>  --  switch to a different chat session
.set-system <TEXT>   --  set a chat session 'system'. who is the ai? how do they respond?
.rm-session          --  deactivate the current session
.rm-session <NAME>   --  deactivate a specific session
.export              --  export the current chat session to csv
.export-csv          --  export the current chat session to csv
.export-json         --  export the current chat session to json
.export-xlsx         --  export the current chat session to xlsx
.export-html         --  export the current chat session to html
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
            filler_str = " "*(44 - (len(version_str)+len(current_time_str)+7))   # 43 total chars in row
            detail_row = f"┃ v{version_str} {filler_str} {current_time_str} ┃"
            banner = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ┏━━━━┓━━━┓━━━┓━━━┓ ┏━━━┓┓ ┏┓━━━┓┓ ┏━┓    ┃
┃ ┃┏┓┏┓┃┏━┓┃┏━┓┃┏━┓┃ ┃┏━┓┃┃ ┃┃┏━━┛┃ ┃ ┃    ┃
┃ ┗┛┃┃┗┛┃ ┃┃┃ ┗┛┃ ┃┃ ┃┗━━┓┗━┛┃┗━━┓┃ ┃ ┃    ┃
┃   ┃┃ ┃┗━┛┃┃ ┏┓┃ ┃┃ ┃━━┓┃┏━┓┃┏━━┛┃ ┏┓┃ ┏┓ ┃
┃  ┏┛┗┓┃┏━┓┃┗━┛┃┗━┛┃━┓┗━┛┃┃ ┃┃┗━━┓┗━┛┃┗━┛┃ ┃
┃  ┗━━┛┗┛ ┗┛━━━┛━━━┛━┛━━━┛┛ ┗┛━━━┛━━━┛━━━┛ ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
{detail_row}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


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
                        self.db.select_table("chat_sessions", where="active = 1")
                    
                    elif cmd.startswith(".models"):
                        models, table = self.ai_engine.get_chat_models()
                        CON.print(table)
                    
                    elif cmd.startswith((".session",)):
                        # CON.print(f"SESSION:  [blue]{self.active_session.name}  [white]([green]{self.active_session.session_id}[white])")
                        # self.db.select_table("chat_content", where=f"session_ref = '{self.active_session.session_id}'")
                        self.db.show_session_content(self.active_session.session_id, self.active_session.name)

                    elif cmd.startswith((".set-session")):
                        session_name: str = cmd.split(" ",maxsplit=1)[1]
                        session_name = session_name.strip()
                        session = self.db.set_active_session(session_name=session_name)
                        self.active_session = session

                    elif cmd.startswith((".set-system")):
                        content: str = cmd.split(" ",maxsplit=1)[1]
                        self.db.set_session_system(self.active_session.session_id, content)
                        CON.print(f"New System Protocal Is Defined for '{self.active_session.name}'")
                    
                    elif cmd.startswith((".rm-session")):
                        content: str = cmd.split(" ",maxsplit=1)
                        if len(content) > 1:
                            sess = content[1]
                            self.db.deactivate_session(session)
                        else:
                            sess = self.active_session.name
                            self.db.deactivate_session(sess)
                            CON.print(f"Session Removed: '{sess}'")
                        
                        session = self.db.set_active_session(session_name="DEFAULT")
                        self.active_session = session

                    elif cmd.startswith(".export"):
                        session_name: str = self.active_session.name
                        guid = self.db.gen_guid()

                        if cmd.startswith(".export-json"):
                            out_path = Path(f"{session_name}_{guid}.json")
                            self.db.export_chat_session(
                                session_id=self.active_session.session_id, 
                                out_path=out_path,
                                ext="json")
                        elif cmd.startswith(".export-csv"):
                            out_path = Path(f"{session_name}_{guid}.csv")
                            self.db.export_chat_session(
                                session_id=self.active_session.session_id, 
                                out_path=out_path,
                                ext="csv")
                        elif cmd.startswith(".export-excel"):
                            out_path = Path(f"{session_name}_{guid}.xlsx")
                            self.db.export_chat_session(
                                session_id=self.active_session.session_id, 
                                out_path=out_path,
                                ext="xlsx")
                        elif cmd.startswith(".export-html"):
                            out_path = Path(f"{session_name}_{guid}.html")
                            self.db.export_chat_session(
                                session_id=self.active_session.session_id, 
                                out_path=out_path,
                                ext="html")
                        else:
                            out_path = Path(f"{session_name}_{guid}.csv")
                            self.db.export_chat_session(
                                session_id=self.active_session.session_id, 
                                out_path=out_path,
                                ext="csv")

                        file_size = os.path.getsize(out_path) / (1024 * 1024)
                        CON.print(f"Export created for '{session_name}' ({file_size:.3f} mb) \n @ [green] {out_path.absolute()}")

                        
                    else:
                        messages = self.ai_engine.get_resp(cmd, messages=messages)
                        content = messages[-2].get("content")
                        self.db.create_chat_content(
                            MChatContent(
                                message_id=self.db.gen_guid(),
                                session_ref=self.active_session.session_id,
                                role=messages[-2].get("role"),
                                content=content,
                                chars=len(content),
                                token_est=len(content)/self.db.token_est_factor,
                                created=datetime.now()
                            )
                        )
                        content = messages[-1].get("content")
                        self.db.create_chat_content(
                            MChatContent(
                                message_id=self.db.gen_guid(),
                                session_ref=self.active_session.session_id,
                                role=messages[-1].get("role"),
                                content=content,
                                chars=len(content),
                                token_est=len(content)/self.db.token_est_factor,
                                created=datetime.now()
                            )
                        )

                        # -- show response
                        if len(messages) > 0:
                            CON.print(f"\n🤖  {messages[-1].get('content')}\n")

                except Exception as error:
                    import traceback
                    traceback.print_exc()
                    # CON.print(error)

        
        print("Wrapping Up Extra Tacos!")
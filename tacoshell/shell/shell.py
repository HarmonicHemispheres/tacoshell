
from .ai import AiEngine
from tacoshell.config import load_config, Config
from pathlib import Path
from rich.console import Console

CON = Console()

class Shell:

    def __init__(self, cfg:Path = None):

        try:
            self.cfg_path = cfg
            self.cfg: Config = load_config(self.cfg_path)

            self.ai_engine = AiEngine(openai_key=self.cfg.openai_key)
        except Exception as error:
            CON.print(f"ERROR setting up shell!\n -> {error}")

    def start(self):
        exit_cmds = ('q', 'exit', 'quit')

        while True:
            try:
                # get command
                cmd = input("🌮 ")

                with CON.status("...."):
    
                    # process command
                    if cmd in exit_cmds:
                        break
                    elif "--eval " in cmd:
                        result = eval(cmd.replace("--eval ",""))
                        CON.print(result)
                    else:
                        resp = self.ai_engine.get_resp(cmd.replace("--code",""))

                        # process response
                        if "--code" in cmd:
                            CON.print(self.ai_engine.get_code(resp))
                        
                        else:
                            CON.print(resp)

            except Exception as error:
                CON.print(error)

        
        print("Exiting Taco Shell")
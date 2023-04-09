
from pydantic import BaseModel
from pathlib import Path
import toml

class Config(BaseModel):
    openai_key: str = None
    openai_chat_model: str = "gpt-3.5-turbo"


    def get(self, key:str):
        return getattr(self, key)


def load_config(path: Path):

    if not path:
        return Config()
    
    with open(Path(path), "r") as fp:
        data = toml.load(fp)

        return Config(**data)

def save_config(config: Config, path: Path):

    cfg_dict = config.dict()

    with open(path, "w") as fp:
        toml.dump(cfg_dict,fp)





from pydantic import BaseModel
from pathlib import Path
import toml

class Config(BaseModel):
    openai_key: str = None


    def get(self, key:str):
        return getattr(self, key)


def load_config(path: Path):

    if not path:
        return Config()
    
    with open(Path(path), "r") as fp:
        data = toml.load(fp)

        return Config(**data)



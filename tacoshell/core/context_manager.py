
from pydantic import BaseModel
from typing import Optional, List, Any
from pathlib import Path
import csv


class Entry(BaseModel):
    pass

class Csv(Entry):
    file: Optional[Path] = None
    dataset_name: str = ""
    columns: List[str] = []
    rows: List[List[Any]] = []

    def load(self, path:Path):
        self.file = Path(path).absolute()
        self.dataset_name = self.file.stem
        with open(self.file, "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for idx, row in enumerate(reader):
                if idx == 0:
                    self.columns = row
                else:
                    self.rows.append(row)
        return self



class ContextManager:
    def __init__(self):
        self._ctx = {}

    def set(self, key:str, entry:Entry):
        self._ctx[key] = entry
        # if isinstance(entry, Csv):
        #     self._ctx['csv'] = {}
        # else:

    def get(self, key:str) -> Entry:
        return self._ctx.get(key)
    
    def delete(self, key:str):
        del self._ctx[key]
    
    def build_context_text(self):
        ctx_text = ":CONTEXT:\n"

        for key, entry in self._ctx.items():
            if isinstance(entry, Csv):
                msg = f"TABLE={entry.dataset_name}, COLUMNS={','.join(entry.columns)}\n"
                ctx_text += msg

        return ctx_text





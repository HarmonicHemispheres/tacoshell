
from pathlib import Path
import duckdb
from pydantic import BaseModel
import pandas
import uuid
from datetime import datetime
from rich.table import Table

# ------------------------------------------ #
# ---------- TABLE MODELS
# ------------------------------------------ #
class MChatSessions(BaseModel):
    session_id: str = ""
    name: str = ""
    created: datetime = datetime.now()
    updated: datetime = datetime.now()


class MODELS:
    chat_sessions = MChatSessions

# ------------------------------------------ #
# ---------- CONTROLLER CLASS
# ------------------------------------------ #
class Database:
    def __init__(self, file: Path = Path("taco.duckdb"), create_new: bool = False):
        self.file: Path = file
        self.tables = {
            "chat_sessions": MChatSessions()
        }
        self.conn = None
        self.connect()
        if create_new:
            if self.file.exists():
                self.drop()
            self.create_ddl()

    def drop(self):
        for tname, table in self.tables.items():
            sql = f"DROP TABLE IF EXISTS {tname};"
            self.conn.execute(sql)
            self.conn.commit()

    def list_tables(self) -> Table:
        table = Table(title=f"Tables for: {self.file}")
        table.add_column("id", style="blue")
        table.add_column("table", style="blue")
        table.add_column("db", style="green")
        table.add_column("rows", style="green")
        table.add_column("columns", style="green")

        sql = f"SELECT * FROM duckdb_tables()"
        self.conn.execute(sql)

        for row in self.conn.fetchall():
            table.add_row(
                str(row[5]),   # table identifier
                str(row[4]),   # table_name
                str(row[0]),   # database
                str(row[9]),   # rows
                str(row[10]),   # columns
            )

        return table

    def connect(self):
        self.conn = duckdb.connect(str(self.file), read_only=False)

    def create_ddl(self):
        for tname, table in self.tables.items():
            t: BaseModel = table
            sql = f"CREATE TABLE {tname}(" 
            for k,v in t.__fields__.items():
                if isinstance(v.default, str):
                    sql += f"{k} VARCHAR,"
                elif isinstance(v.default, int):
                    sql += f"{k} INTEGER,"
                elif isinstance(v.default, datetime):
                    sql += f"{k} TIMESTAMP,"

            sql = sql[0:-1]
            sql += ");"
            self.conn.execute(sql)
            self.conn.commit()
            

    def load_csv(self, path: Path):
        # duckdb.read_csv(str(Path(path)), header=True, encoding="utf-8", )
        pass

    # ------------------------------------------ #
    # ---------- CRUD
    # ------------------------------------------ #
    def create_chat_session(self, session: MChatSessions):
        sql = self.get_insert_sql("chat_sessions", session)
        self.conn.execute(sql)
        self.conn.commit()

        self.conn.execute(f"SELECT * FROM chat_sessions")

    # ------------------------------------------ #
    # ---------- HELPER FUNCTIONS
    # ------------------------------------------ #
    def gen_guid(self):
        return str(uuid.uuid4())

    def get_insert_sql(self, table:str, model:BaseModel):
        vals = ",".join([f"'{getattr(model,k)}'" for k in model.__fields__.keys()])
        return f"INSERT INTO {table} VALUES ({vals});"

    def select_table(self, name: str):
        sql = f"SELECT * FROM {name}"
        result = self.conn.sql(sql)
        result.show()
    

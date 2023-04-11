
from pathlib import Path
import duckdb
from pydantic import BaseModel
import pandas
import json
import uuid
import pkg_resources
from datetime import datetime
from rich.table import Table
import rich

# ------------------------------------------ #
# ---------- TABLE MODELS
# ------------------------------------------ #
class MChatSessions(BaseModel):
    session_id: str = ""
    name: str = ""
    is_active: bool = False
    created: datetime = datetime.now()
    updated: datetime = datetime.now()

class MChatContent(BaseModel):
    message_id: str = ""
    session_ref: str = ""
    role: str = ""    # user, system, assistant
    content: str = ""
    chars: int = 0
    token_est: int = 0
    created: datetime = datetime.now()

class MAbout(BaseModel):
    created: datetime = datetime.now()
    taco_version: str = ""

class MFiles(BaseModel):
    file_id: str = ""
    name: str = ""
    type: str = ""
    source_path: str = ""
    content: str = ""
    created: datetime = datetime.now()
    updated: datetime = datetime.now()





# ------------------------------------------ #
# ---------- CONTROLLER CLASS
# ------------------------------------------ #
class Database:
    def __init__(self, file: Path = Path("taco.duckdb"), create_new: bool = False):
        self.file: Path = file
        self.tables = {
            "chat_sessions": MChatSessions(),
            "chat_content": MChatContent(),
            "about": MAbout(),
            "files": MFiles()
        }
        self.conn = None
        try:
            self.connect()
        except:
            raise Exception(f"Cannot connect to DB: {self.file}")
        if create_new:
            if self.file.exists():
                self.drop()
            self.create_ddl()
            self.setup_static()

    def setup_static(self):
        # create info
        about = MAbout(taco_version=pkg_resources.get_distribution("tacoshell").version)
        sql = self.get_insert_sql("about",model=about)
        self.conn.execute(sql)
        self.conn.commit()

        # 

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
                elif isinstance(v.default, bool):
                    sql += f"{k} BOOLEAN,"
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
    
    def create_chat_content(self, content: MChatContent):
        sql = self.get_insert_sql("chat_content", content)
        self.conn.execute(sql)
        self.conn.commit()

    def select_session(self, name:str, session_id:str="") -> MChatSessions:
        sql = f"SELECT * FROM chat_sessions WHERE name = '{name}' OR session_id = '{session_id}'"
        self.conn.execute(sql)
        record = self.conn.fetchone()
        if record:
            return MChatSessions(
                session_id=record[0],
                name=record[1],
                is_active=record[2],
                created=record[3],
                updated=record[4],
                )
        else:
            return None

    def set_active_session(self,session_name:str) -> MChatSessions:
        
        # -- set old active session to inactive
        current_active_session = self.get_active_session()
        if current_active_session:
            sql = f"UPDATE chat_sessions SET is_active=FALSE WHERE session_id = '{current_active_session.session_id}'"
            self.conn.execute(sql)
            self.conn.commit()
            
        # -- create or set new active session
        session: MChatSessions = self.select_session(session_name)
        if session:
            sql = f"UPDATE chat_sessions SET is_active=TRUE WHERE session_id = '{session.session_id}'"
            self.conn.execute(sql)
            self.conn.commit()

        else:
            session = MChatSessions(
                        session_id=self.gen_guid(),
                        name=session_name,
                        is_active=True
                      )
            self.create_chat_session(session)

        return session
    
        
    def select_session_content(self, session_id, as_dict=True):
        cursor = self.conn.cursor()
        cursor.execute(f"""
        SELECT 
            message_id,
            session_ref,
            role,
            content 
        FROM chat_content 
        WHERE session_ref = '{session_id}'
        """)

        data = [row for row in cursor.fetchall()]

        if as_dict:
            return [
                {"role":row[2], "content":row[3]} for row in data
            ]
        else:
            return data
        
    def get_active_session(self) -> MChatSessions:
        sql = f"SELECT * FROM chat_sessions WHERE is_active = TRUE"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        record = cursor.fetchone()
        if not record:
            return None
        return MChatSessions(
            session_id=record[0],
            name=record[1],
            is_active=record[2],
            created=record[3],
            updated=record[4],
            )


    # ------------------------------------------ #
    # ---------- HELPER FUNCTIONS
    # ------------------------------------------ #
    def gen_guid(self):
        return self.gen_guid_long()[0:7]
    
    def gen_guid_long(self):
        return str(uuid.uuid4())

    def get_insert_sql(self, table:str, model:BaseModel):
        values = []
        for k in model.__fields__.keys():
            formatted = str(getattr(model,k)).replace("'", "''")

            v = f"'{formatted}'" 
            values.append(v)

        vals = ",".join(values)
        return f"INSERT INTO {table} VALUES ({vals});"

    def select_table(self, name: str, where:str = None):

        if where:
            sql = f"SELECT * FROM {name} WHERE {where}"
            result = self.conn.sql(sql)
        else:
            sql = f"SELECT * FROM {name}"
            result = self.conn.sql(sql)
        result.show()

    def show_session_content(self, session_id, session_name):

        sql = f"""
SELECT 
    session_ref,
    message_id,
    created, 
    chars,
    role,
    token_est,
    content
FROM chat_content 
WHERE session_ref = '{session_id}'
"""
        cursor = self.conn.cursor()
        cursor.execute(sql)

        table = Table(title=f"Session: {session_name} ({session_id})")
        table.add_column("message_id", style="blue")
        table.add_column("created", style="white")
        table.add_column("chars", style="green")
        table.add_column("token_est", style="green")
        table.add_column("role", style="green")
        table.add_column("content", style="white", overflow="fold")

        for row in cursor.fetchall():
            table.add_row(
                str(row[1]),
                row[2].strftime('%Y-%m-%d %H:%M'),
                str(row[3]),
                str(row[4]),
                str(row[5]),
                str(row[6]),
            )

        rich.print(table)


    ##########################################
    # --------  EXPORTERS
    ##########################################
    def export_chat_session(self, session_id:str, out_path: Path, ext="csv"):
        sql = f"""
SELECT 
    session_ref,
    message_id,
    created, 
    chars,
    role,
    token_est,
    content
FROM chat_content 
WHERE session_ref = '{session_id}'
        """
        cursor = self.conn.cursor()
        cursor.execute(sql)
        df = cursor.df()

        if ext == "csv":
            df.to_csv(out_path)
        elif ext == "json":
            df.to_json(out_path, indent=2, orient="records")
        elif ext == "xlsx":
            df.to_excel(out_path)
        elif ext == "html":
            df.to_html(out_path)

        
    

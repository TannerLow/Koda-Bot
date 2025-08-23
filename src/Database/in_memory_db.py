from typing import Any

from .database import Database
from .schema import Schema

class InMemoryDatabase(Database):

    def __init__(self, name: str):
        self.name = name
        self.db = Schema()

    def get_record(self, table: str, key: Any) -> Any:
        db_table: Any = self.get_table(table)
        if key not in db_table:
            raise KeyError(f"Key '{key}' not in table '{table}'")

        return db_table.get(key)
    
    def set_record(self, table: str, key: Any, data: Any) -> None:
        db_table: dict = self.get_table(table)
        db_table[key] = data

    def get_table(self, table: str) -> dict:
        db_table: dict = getattr(self.db, table)

        if db_table is None:
            raise KeyError(f"Table '{table}' not in db. Available tables: {self.db.keys()}")

        return db_table
    
    def get_table_names(self) -> list[str]:
        return list(self.db.model_dump().keys())
    
    def get_schema(self) -> Schema:
        return self.db

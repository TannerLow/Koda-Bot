from typing import Any

class InMemoryDatabase:

    def __init__(self, name: str):
        self.name = name
        self.db = {}

    def get_record(self, table: str, key: Any) -> dict:
        db_table: dict = self.get_table(table)
        if key not in db_table:
            raise KeyError(f"Key '{key}' not in table '{table}'")

        return db_table.get(key)
    
    def set_record(self, table: str, key: Any, data: Any) -> None:
        db_table: dict = self.get_table(table)
        db_table[key] = data

    def create_table(self, table: str) -> None:
        if table not in self.db:
            self.db[table] = {}

    def get_table(self, table: str) -> dict:
        db_table: dict = self.db.get(table)

        if db_table is None:
            raise KeyError(f"Table '{table}' not in db. Available tables: {self.db.keys()}")

        return db_table

from typing import Any

class Database:

    def __init__(self):
        raise NotImplementedError("Attempt to use an abstract class")

    def get_record(self, table: str, key: Any) -> Any:
        raise NotImplementedError("Attempt to use an abstract class")
    
    def set_record(self, table: str, key: Any, data: Any) -> None:
        raise NotImplementedError("Attempt to use an abstract class")
    
    def create_table(self, table: str) -> None:
        raise NotImplementedError("Attempt to use an abstract class")
    
    def get_table(self, table: str) -> Any:
        raise NotImplementedError("Attempt to use an abstract class")

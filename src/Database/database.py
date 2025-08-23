from typing import Any
from abc import ABC, abstractmethod

from .schema import Schema

class Database(ABC):
    
    @abstractmethod
    def get_record(self, table: str, key: Any) -> Any:
        pass
    
    @abstractmethod
    def set_record(self, table: str, key: Any, data: Any) -> None:
        pass
    
    @abstractmethod
    def get_table(self, table: str) -> Any:
        pass
    
    @abstractmethod
    def get_table_names(self) -> list[str]:
        pass

    @abstractmethod
    def get_schema(self) -> Any:
        pass

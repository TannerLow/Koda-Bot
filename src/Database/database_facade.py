from abc import ABC, abstractmethod

from ..API.model import (
    Stats,
    User
)

class DatabaseFacade(ABC):

    @abstractmethod
    def create_tables(self):
        pass

    @abstractmethod
    def get_stats(self, user_id: int) -> Stats:
        pass
    
    @abstractmethod
    def create_missing_user_data(self, user: User) -> None:
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> User:
        pass
    
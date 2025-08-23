from abc import ABC, abstractmethod
from typing import Optional

from ..API.model import (
    Stats,
    User,
    Checkin
)

class DatabaseFacade(ABC):

    @abstractmethod
    def get_stats(self, user_id: int) -> Stats:
        pass
    
    @abstractmethod
    def create_missing_user_data(self, user: User) -> None:
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> User:
        pass

    @abstractmethod
    def create_checkin(self, checkin: Checkin) -> str:
        pass

    @abstractmethod
    def update_users_last_checkin(self, user_id: int, new_checkin_id: int, checkin: Checkin) -> None:
        pass
    
    @abstractmethod
    def update_users_github_name(self, user_id: int, github_name: str) -> None:
        pass

    @abstractmethod
    def save_db(self, permanent: bool = False) -> None:
        pass

    @abstractmethod
    def load_db(self) -> bool:
        pass

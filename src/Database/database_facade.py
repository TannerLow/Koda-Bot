from abc import ABC, abstractmethod

from ..API.model import (
    Stats,
    User,
    Checkin
)

class DatabaseFacade(ABC):

    # @abstractmethod
    # def create_tables(self):
    #     pass

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
    def save_db(self) -> None:
        pass

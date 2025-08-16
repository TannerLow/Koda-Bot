from uuid import uuid4

from .database_facade import DatabaseFacade
from .database import Database
from ..API.model import (
    Stats,
    User,
    LevelingSettings,
    Checkin
)
from ..Logging.logger import Logger

LOGGER = Logger(__file__, "debug")

class InMemoryDatabaseFacade(DatabaseFacade):

    def __init__(self, database: Database):
        self.database = database

    def create_tables(self):
        self.database.create_table('stats')
        self.database.create_table('users')
        self.database.create_table('checkins')
        self.database.create_table('user_checkins')

    def get_stats(self, user_id: int) -> Stats:
        stats_dict: dict = self.database.get_record('stats', user_id)
        return Stats.model_validate(stats_dict)
    
    def create_missing_user_data(self, user: User) -> None:
        try:
            self.database.get_record('users', user.id)
            # TODO update info where necessary since dynamic user data may have changed since last time
        except KeyError:
            user_dict: dict = user.model_dump()
            LOGGER.info(f"Creating a new User in users: {user_dict}")
            self.database.set_record('users', user.id, user_dict)
        
        try:
            self.database.get_record('stats', user.id)
        except KeyError:
            stats_dict: dict = Stats(
                xp=0,
                total_xp_needed=LevelingSettings.xp_to_next_level(1),
                level=1
            ).model_dump()
            LOGGER.info(f"Creating a new Stats in stats: {stats_dict}")
            self.database.set_record('stats', user.id, stats_dict)

    def get_user(self, user_id: int) -> User:
        user_dict: dict = self.database.get_record('users', user_id)
        return User.model_validate(user_dict)
        
    def give_xp(self, user_id: int, amount: int) -> None:
        stats_dict: dict = self.database.get_record('stats', user_id)
        stats: Stats = Stats.model_validate(stats_dict)

        stats.xp += amount
        if (stats.total_xp_needed - stats.xp) <= 0:
            stats.level += 1
            stats.xp = 0
            stats.total_xp_needed = LevelingSettings.xp_to_next_level(stats.level)
        
        self.database.set_record('stats', user_id, stats.model_dump())
        LOGGER.debug(f"Updated user {user_id}'s stats: {stats.model_dump_json()}")

    def create_checkin(self, checkin: Checkin) -> int:
        new_checkin_id: str = str(uuid4())
        self.database.set_record('checkins', new_checkin_id, checkin.model_dump())
        LOGGER.info(f"Created new checkin: {new_checkin_id}")
        return new_checkin_id

    def update_users_last_checkin(self, user_id: int, new_checkin_id: int, checkin: Checkin) -> None:
        user: User = self.get_user(user_id)
        user.last_checkin_id = new_checkin_id
        user.last_checkin = checkin
        self.database.set_record('users', user_id, user.model_dump())
        LOGGER.info(f"Updated user {user_id}'s last checkin to: {new_checkin_id}")

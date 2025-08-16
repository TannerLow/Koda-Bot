import os
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Optional

from ..Logging.logger import Logger
from ..Database.database import Database
from .model import (
    Stats,
    User,
    Checkin
)
from .exceptions import NewUserError

LOGGER = Logger(__file__, "debug")

class Koda:

    def __init__(self, templates_dir_path: str, database: Database):
        if not os.path.exists(templates_dir_path):
            raise NotADirectoryError(f"Couldn't find Koda templates: {templates_dir_path}")
        
        self.templates = self.load_templates(templates_dir_path)
        self.database = database
        self.user_cache = set()

        self.setup_database()

    def load_templates(self, templates_dir_path: str) -> dict[str, str]:
        file_contents = {}

        # Iterate over all items in the directory
        for filename in os.listdir(templates_dir_path):
            file_path = os.path.join(templates_dir_path, filename)

            # Skip directories, only read files
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    file_contents[filename] = f.read()

        LOGGER.debug(file_contents)
        return file_contents
    
    def setup_database(self) -> None:
        self.database.create_table('stats')
        self.database.create_table('users')
        self.database.create_table('checkins')
        self.database.create_table('user_checkins')

    def get_help_text(self) -> str:
        return self.templates['help.txt']
    
    def get_stats(self, user_id: int) -> Stats:
        if self.new_user_detected(user_id):
            raise NewUserError(f"New user detected: {user_id}")

        stats_dict: dict = self.database.get_record('stats', user_id)
        LOGGER.debug(f"Retrieved stats from db: {stats_dict}")
        return Stats.model_validate(stats_dict)
    
    def new_user_detected(self, user_id: int) -> bool:
        """ True if user was not in the cache
        """
        if user_id not in self.user_cache:
            LOGGER.debug(f"User was not in cache: {user_id}")
            return True
        
        return False
    
    def establish_new_user(self, user: User) -> None:
        """ Data may exist but user was not cached so create data where necessary to avoid missing records
        """
        self.user_cache.add(user.id)

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
                xp_to_level=100,
                level=1
            ).model_dump()
            LOGGER.info(f"Creating a new Stats in stats: {stats_dict}")
            self.database.set_record('stats', user.id, stats_dict)

    def checkin(self, user_id: int, checkin: Checkin) -> Optional[timedelta]:
        if self.new_user_detected(user_id):
            raise NewUserError(f"New user detected: {user_id}")
        
        user_dict: dict = self.database.get_record('users', user_id)
        user: User = User.model_validate(user_dict)
        if user.last_checkin is not None:
            last_checkin_dict: dict = self.database.get_record('checkins', user.last_checkin)
            last_checkin: Checkin = Checkin.model_validate(last_checkin_dict)

            if self._checkin_is_too_soon(last_checkin, checkin.date):
                # TODO allow premature checkins that dont give xp
                LOGGER.debug(f"User {user_id} attempted to checkin early")
                return timedelta(hours=16) - (checkin.date - last_checkin.date)
        
        new_checkin_id: str = str(uuid4())
        self.database.set_record('checkins', new_checkin_id, checkin.model_dump())
        LOGGER.info(f"Created new checkin for user {user_id}: {new_checkin_id}")

        user.last_checkin = new_checkin_id
        self.database.set_record('users', user_id, user.model_dump())
        LOGGER.info(f"Updated user {user_id}'s last checkin to: {new_checkin_id}")
        return None # no cooldown remaining

    def _checkin_is_too_soon(self, last_checkin: Checkin, new_checkin_time: datetime) -> bool:
        """ 16 hour cooldowns on checkins
        """
        difference: timedelta = new_checkin_time - last_checkin.date
        LOGGER.debug(f"Checkin time difference: {difference}")
        return difference < timedelta(hours=16)
    
    def give_xp(self, user_id: int, amount: int) -> None:
        stats_dict: dict = self.database.get_record('stats', user_id)
        stats: Stats = Stats.model_validate(stats_dict)

        stats.xp += amount
        stats.xp_to_level -= amount
        if stats.xp_to_level <= 0:
            stats.level += 1
            stats.xp = 0
            stats.xp_to_level = 100
        
        self.database.set_record('stats', user_id, stats.model_dump())
        LOGGER.debug(f"Updated user {user_id}'s stats: {stats.model_dump_json()}")

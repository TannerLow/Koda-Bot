import os
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Optional

from ..Logging.logger import Logger
from ..Database.database_facade import DatabaseFacade
from .model import (
    Stats,
    User,
    Checkin,
    CheckinSettings,
    LevelingSettings
)
from .exceptions import NewUserError

LOGGER = Logger(__file__, "debug")

class Koda:

    def __init__(
        self, 
        templates_dir_path: str, 
        database_facade: DatabaseFacade, 
        checkin_settings: CheckinSettings,
        leveling_settings: LevelingSettings
    ):
        if not os.path.exists(templates_dir_path):
            raise NotADirectoryError(f"Couldn't find Koda templates: {templates_dir_path}")
        
        self.checkin_settings = checkin_settings
        self.leveling_settings = leveling_settings
        self.templates = self.load_templates(templates_dir_path)
        self.database_facade = database_facade
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
        self.database_facade.create_tables()
        # NOTE if I dont add more then I can just de-functionify

    def get_help_text(self) -> str:
        return self.templates['help.txt']
    
    def get_stats(self, user_id: int) -> Stats:
        if self.new_user_detected(user_id):
            raise NewUserError(f"New user detected: {user_id}")

        stats: Stats = self.database_facade.get_stats(user_id)
        
        LOGGER.debug(f"Retrieved stats from db: {stats.model_dump_json()}")
        return stats
    
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
        self.database_facade.create_missing_user_data(user)

    def checkin(self, user_id: int, checkin: Checkin) -> Optional[timedelta]:
        if self.new_user_detected(user_id):
            raise NewUserError(f"New user detected: {user_id}")
        
        #get user
        user: User = self.database_facade.get_user(user_id)

        if user.last_checkin is not None:
            # last_checkin_dict: dict = self.database.get_record('checkins', user.last_checkin)
            # last_checkin: Checkin = Checkin.model_validate(last_checkin_dict)

            if self._checkin_is_too_soon(user.last_checkin, checkin.date):
                # TODO allow premature checkins that dont give xp to be logged to history
                LOGGER.debug(f"User {user_id} attempted to checkin early")
                return self.checkin_settings.base_cooldown - (checkin.date - user.last_checkin.date)
        
        # create new checkin
        new_checkin_id: int = self.database_facade.create_checkin(checkin)

        # update last checkin
        self.database_facade.update_users_last_checkin(user.id, new_checkin_id, checkin)
        return None # no cooldown remaining

    def _checkin_is_too_soon(self, last_checkin: Checkin, new_checkin_time: datetime) -> bool:
        """ Checkins have a cooldown to prevent spamming for XP GAINZ!!!
        """
        difference: timedelta = new_checkin_time - last_checkin.date
        LOGGER.debug(f"Checkin time difference: {difference}")
        return difference < self.checkin_settings.base_cooldown
    
    def give_xp(self, user_id: int, amount: int) -> None:
        self.database_facade.give_xp(user_id, amount)

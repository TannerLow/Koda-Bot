from uuid import uuid4
from pathlib import Path
import os
from typing import Optional
import time

from .database_facade import DatabaseFacade
from .database import Database
from .model import DatabaseSettings
from ..API.model import (
    Stats,
    User,
    LevelingSettings,
    Checkin
)
from ..Logging.logger import Logger

LOGGER = Logger(__file__, "debug")

class InMemoryDatabaseFacade(DatabaseFacade):

    def __init__(
        self, 
        database: Database,
        database_settings: DatabaseSettings
    ):
        self.database = database
        self.database_settings = database_settings

    def get_stats(self, user_id: int) -> Stats:
        return self.database.get_record('stats', user_id)
    
    def create_missing_user_data(self, user: User) -> None:
        try:
            self.database.get_record('users', user.id)
            # TODO update info where necessary since dynamic user data may have changed since last time
        except KeyError:
            LOGGER.info(f"Creating a new User in users: {user.model_dump()}")
            self.database.set_record('users', user.id, user)
        
        try:
            self.database.get_record('stats', user.id)
        except KeyError:
            stats = Stats(
                xp=0,
                total_xp_needed=LevelingSettings.xp_to_next_level(1),
                level=1
            )
            LOGGER.info(f"Creating a new Stats in stats: {stats.model_dump()}")
            self.database.set_record('stats', user.id, stats)

    def get_user(self, user_id: int) -> User:
        user: User = self.database.get_record('users', user_id)
        LOGGER.debug(f"Retrieved user from db: {user.model_dump()}")
        return User.model_validate(user)
        
    def give_xp(self, user_id: int, amount: int) -> None:
        stats: Stats = self.database.get_record('stats', user_id)

        stats.xp += amount
        if (stats.total_xp_needed - stats.xp) <= 0:
            stats.level += 1
            stats.xp = 0
            stats.total_xp_needed = LevelingSettings.xp_to_next_level(stats.level)
        
        self.database.set_record('stats', user_id, stats)
        LOGGER.debug(f"Updated user {user_id}'s stats: {stats.model_dump_json()}")

    def create_checkin(self, checkin: Checkin) -> str:
        new_checkin_id: str = str(uuid4())
        self.database.set_record('checkins', new_checkin_id, checkin)
        LOGGER.info(f"Created new checkin: {new_checkin_id}")
        return new_checkin_id

    def update_users_last_checkin(self, user: User, new_checkin_id: int, checkin: Checkin) -> None:
        user: User = self.get_user(user.id)
        user.last_checkin_id = new_checkin_id
        user.last_checkin = checkin

        self.database.set_record('users', user.id, user)

        LOGGER.info(f"Updated user {user.id}'s last checkin to: {new_checkin_id}")
        LOGGER.debug(f"New user data: {user.model_dump_json()}")

    def update_users_github_name(self, user_id: int, github_name: str) -> None:
        user: User = self.get_user(user_id)
        user.github_name = github_name
        self.database.set_record('users', user_id, user)
        LOGGER.info(f"Set user {user_id}'s github name to {github_name}")

    def save_db(self, permanent: bool = False) -> None:
        if permanent:
            folder_path = Path(self.database_settings.save_folder)
            stem, suffix = Path(self.database_settings.save_filename).stem, Path(self.database_settings.save_filename).suffix
            timestamp_str = str(int(time.time()))
            filename = Path(f"{stem}_{timestamp_str}{suffix}")
            filepath: Path = folder_path / filename

        else:
            filepath: Path = self._get_save_filename()

        with open(filepath, 'w') as file:
            file.write(self.database.get_schema().model_dump_json())

    def load_db(self) -> bool:
        filepath: Path = self._get_latest_filename()

        if not filepath or not os.path.exists(filepath):
            return False

        schema_type: type = type(self.database.get_schema())
        with open(filepath, 'r') as file:
            self.database.db = schema_type.model_validate_json(file.read())
            return True
        
        return False

    def _get_save_filename(self) -> Path:
        """
        Save to 1 of 3 save files on a rolling basis
        """
        folder_path = Path(self.database_settings.save_folder)
        folder_path.mkdir(parents=True, exist_ok=True)

        stem, suffix = Path(self.database_settings.save_filename).stem, Path(self.database_settings.save_filename).suffix

        # define the 3 rolling filenames
        candidates = [folder_path / f"{stem}_{i}{suffix}" for i in range(1, 4)]

        # pick the oldest file (or a missing one)
        oldest_file = min(
            candidates,
            key=lambda f: f.stat().st_mtime if f.exists() else float("-inf")
        )

        return oldest_file

    
    def _get_latest_filename(self) -> Optional[Path]:
        """
        Get the most recently modified file in the save folder.
        """
        folder_path = Path(self.database_settings.save_folder)

        if not folder_path.exists():
            return None

        # grab only files (ignore subfolders)
        files = [f for f in folder_path.iterdir() if f.is_file()]
        if not files:
            return None

        # pick the newest one by modified time
        return max(files, key=lambda f: f.stat().st_mtime)

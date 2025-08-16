from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel
class Stats(BaseModel):
    xp: int
    total_xp_needed: int
    level: int

class Checkin(BaseModel):
    user_id: int
    date: datetime
    proof: str

class User(BaseModel):
    id: int
    last_check_id: Optional[int] = None
    last_checkin: Optional[Checkin] = None

class CheckinSettings(BaseModel):
    base_cooldown: timedelta

class LevelingSettings(BaseModel):
    checkin_reward: int

    @staticmethod
    def xp_to_next_level(current_level: int) -> int:
        return current_level * 500

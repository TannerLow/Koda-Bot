from datetime import datetime
from typing import Optional

from pydantic import BaseModel
class Stats(BaseModel):
    xp: int
    xp_to_level: int
    level: int

class User(BaseModel):
    id: int
    last_checkin: Optional[str] = None

class Checkin(BaseModel):
    user_id: int
    date: datetime
    proof: str

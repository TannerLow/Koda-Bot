from pydantic import BaseModel

from ..API.model import (
    User,
    Stats,
    Checkin
)


class Schema(BaseModel):
    users: dict[str, User] = {}
    stats: dict[str, Stats] = {}
    checkins: dict[str, Checkin] = {}
    user_checkins: dict[str, str] = {}

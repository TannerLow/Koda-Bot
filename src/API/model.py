from datetime import datetime, timedelta, date
from typing import Optional
from enum import Enum

from pydantic import BaseModel


class Stats(BaseModel):
    xp: int
    total_xp_needed: int
    level: int

class ProofType(Enum):
    Contribution = 'Contribution'
    No_proof = 'No_proof',
    Note = 'Note'

class Checkin(BaseModel):
    user_id: str
    date: datetime
    proof: str
    proof_type: Optional[ProofType] = None

class GithubContributionDay(BaseModel):
    date: date
    count: int

class User(BaseModel):
    id: str
    last_checkin_id: Optional[str] = None
    last_checkin: Optional[Checkin] = None
    github_name: Optional[str] = None
    last_github_contribution: Optional[GithubContributionDay] = None

class CheckinSettings(BaseModel):
    base_cooldown: timedelta

class LevelingSettings(BaseModel):
    checkin_reward: int

    @staticmethod
    def xp_to_next_level(current_level: int) -> int:
        return current_level * 500

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LeaderboardEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rank: int
    user_id: str
    score: float
    updated_at: datetime


class TopScoresResponse(BaseModel):
    game_id: str
    entries: list[LeaderboardEntry]


class UserContextResponse(BaseModel):
    game_id: str
    user_id: str
    rank: int | None
    score: float | None
    above: list[LeaderboardEntry]
    below: list[LeaderboardEntry]

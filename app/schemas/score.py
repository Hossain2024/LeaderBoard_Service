from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ScoreSubmitRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    game_id: str = Field(..., min_length=1)
    score: float = Field(..., ge=0)


class ScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    game_id: str
    score: float
    updated_at: datetime
    is_new_high_score: bool

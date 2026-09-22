from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.score import ScoreResponse, ScoreSubmitRequest
from app.services import leaderboard_service

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("", response_model=ScoreResponse, status_code=200)
def submit_score(payload: ScoreSubmitRequest, db: Session = Depends(get_db)):
    return leaderboard_service.submit_score(db, payload)

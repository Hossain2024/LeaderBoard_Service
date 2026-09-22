from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.leaderboard import TopScoresResponse, UserContextResponse
from app.schemas.score import ScoreResponse, ScoreSubmitRequest
from app.services import leaderboard_service

router = APIRouter(tags=["leaderboard"])


@router.post("/scores", response_model=ScoreResponse, status_code=200)
def submit_score(payload: ScoreSubmitRequest, db: Session = Depends(get_db)):
    return leaderboard_service.submit_score(db, payload)


@router.get("/leaderboard/{game_id}/top", response_model=TopScoresResponse)
def get_top_scores(
    game_id: str,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return leaderboard_service.get_top_scores(db, game_id, limit)


@router.get(
    "/leaderboard/{game_id}/users/{user_id}/context",
    response_model=UserContextResponse,
)
def get_user_context(
    game_id: str,
    user_id: str,
    window: int = Query(default=2, ge=1, le=20),
    db: Session = Depends(get_db),
):
    return leaderboard_service.get_user_context(db, game_id, user_id, window)

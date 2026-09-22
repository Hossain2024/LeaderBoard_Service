from sqlalchemy.orm import Session

from app.repositories import leaderboard_repository
from app.schemas.score import ScoreResponse, ScoreSubmitRequest


def submit_score(db: Session, payload: ScoreSubmitRequest) -> ScoreResponse:
    existing = leaderboard_repository.get_score(db, payload.user_id, payload.game_id)

    if existing is None:
        record = leaderboard_repository.create_score(
            db, payload.user_id, payload.game_id, payload.score
        )
        is_new_high_score = True
    elif payload.score > existing.score:
        record = leaderboard_repository.update_score(db, existing, payload.score)
        is_new_high_score = True
    else:
        record = existing
        is_new_high_score = False

    return ScoreResponse(
        user_id=record.user_id,
        game_id=record.game_id,
        score=record.score,
        updated_at=record.updated_at,
        is_new_high_score=is_new_high_score,
    )

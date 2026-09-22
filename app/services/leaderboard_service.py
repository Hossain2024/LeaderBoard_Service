from sqlalchemy.orm import Session

from app.repositories import leaderboard_repository
from app.schemas.leaderboard import (
    LeaderboardEntry,
    TopScoresResponse,
    UserContextResponse,
)
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


def get_top_scores(db: Session, game_id: str, limit: int) -> TopScoresResponse:
    rows = leaderboard_repository.get_top_scores(db, game_id, limit)
    entries = [
        LeaderboardEntry(
            rank=row.rank,
            user_id=row.user_id,
            score=row.score,
            updated_at=row.updated_at,
        )
        for row in rows
    ]
    return TopScoresResponse(game_id=game_id, entries=entries)


def get_user_context(
    db: Session, game_id: str, user_id: str, window: int
) -> UserContextResponse:
    target, above_rows, below_rows = leaderboard_repository.get_user_context(
        db, game_id, user_id, window
    )

    if target is None:
        return UserContextResponse(
            game_id=game_id,
            user_id=user_id,
            rank=None,
            score=None,
            above=[],
            below=[],
        )

    def to_entry(row) -> LeaderboardEntry:
        return LeaderboardEntry(
            rank=row.rank,
            user_id=row.user_id,
            score=row.score,
            updated_at=row.updated_at,
        )

    return UserContextResponse(
        game_id=game_id,
        user_id=user_id,
        rank=target.rank,
        score=target.score,
        above=[to_entry(row) for row in above_rows],
        below=[to_entry(row) for row in below_rows],
    )

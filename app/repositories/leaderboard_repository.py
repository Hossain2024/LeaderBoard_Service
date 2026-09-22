from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.score import Score


def get_score(db: Session, user_id: str, game_id: str) -> Score | None:
    return (
        db.query(Score)
        .filter(Score.user_id == user_id, Score.game_id == game_id)
        .first()
    )


def create_score(db: Session, user_id: str, game_id: str, score: float) -> Score:
    record = Score(user_id=user_id, game_id=game_id, score=score)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_score(db: Session, record: Score, score: float) -> Score:
    record.score = score
    db.commit()
    db.refresh(record)
    return record


def get_top_scores(db: Session, game_id: str, limit: int):
    ranked = (
        select(
            Score.user_id,
            Score.score,
            Score.updated_at,
            func.rank().over(order_by=Score.score.desc()).label("rank"),
        )
        .where(Score.game_id == game_id)
        .subquery()
    )
    stmt = select(ranked).order_by(ranked.c.rank).limit(limit)
    return db.execute(stmt).all()

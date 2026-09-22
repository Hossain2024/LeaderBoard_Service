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


def _ranked_subquery(game_id: str):
    return (
        select(
            Score.user_id,
            Score.score,
            Score.updated_at,
            func.rank().over(order_by=Score.score.desc()).label("rank"),
            func.row_number()
            .over(order_by=[Score.score.desc(), Score.user_id.asc()])
            .label("position"),
        )
        .where(Score.game_id == game_id)
        .subquery()
    )


def get_top_scores(db: Session, game_id: str, limit: int):
    ranked = _ranked_subquery(game_id)
    stmt = select(ranked).order_by(ranked.c.position).limit(limit)
    return db.execute(stmt).all()


def get_user_context(db: Session, game_id: str, user_id: str, window: int):
    ranked = _ranked_subquery(game_id)

    target = db.execute(
        select(ranked).where(ranked.c.user_id == user_id)
    ).first()
    if target is None:
        return None, [], []

    above_stmt = (
        select(ranked)
        .where(ranked.c.position < target.position)
        .order_by(ranked.c.position.desc())
        .limit(window)
    )
    above = list(reversed(db.execute(above_stmt).all()))

    below_stmt = (
        select(ranked)
        .where(ranked.c.position > target.position)
        .order_by(ranked.c.position.asc())
        .limit(window)
    )
    below = db.execute(below_stmt).all()

    return target, above, below

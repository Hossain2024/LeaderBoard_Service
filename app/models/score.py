from sqlalchemy import Column, DateTime, Float, Integer, String, UniqueConstraint, func

from app.database import Base


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_user_game"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    game_id = Column(String, nullable=False, index=True)
    score = Column(Float, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

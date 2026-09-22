from fastapi import FastAPI

from app.database import Base, engine
from app.routers import leaderboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leaderboard Service")

app.include_router(leaderboard.router)


@app.get("/health")
def health():
    return {"status": "ok", "database": engine.dialect.name}

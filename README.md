# LeaderBoard Service

A production-ready REST API for a global gaming leaderboard. It ranks users by score, per game, in real time — built with FastAPI, SQLAlchemy, and Postgres (SQLite for local dev).

## Features

- **Submit Score** — accept a score update for a user in a given game.
- **Top X Rank** — return the top N ranked users for a game.
- **User Context** — return a user's rank plus the users immediately above/below them.

## Architecture

The service follows a layered architecture to keep HTTP concerns, business rules, and data access independent of each other:

```
Request
  │
  ▼
Router (app/routers)        → HTTP layer: parses requests, returns responses
  │
  ▼
Service (app/services)      → business rules: ranking logic, score rules
  │
  ▼
Repository (app/repositories) → data access: SQL queries only, no business logic
  │
  ▼
Model (app/models)          → SQLAlchemy ORM tables
  │
  ▼
Database (Postgres / SQLite)
```

**Why this separation:** each layer can be tested, reasoned about, and changed independently. The router doesn't know how ranking is computed; the service doesn't know or care whether data comes from Postgres or SQLite; the repository doesn't know why a query is being run. In a real code review, this is the main thing to point to — no SQL in routers, no HTTP concerns in services, no business rules in repositories.

### Project layout

```
app/
├── main.py                      # FastAPI app instance, table creation, health check
├── config.py                    # environment-driven settings (DATABASE_URL, etc.)
├── database.py                  # SQLAlchemy engine/session, get_db dependency
├── exceptions.py                # custom exceptions (reserved for future use)
├── cache.py                     # reserved for a Redis-backed cache (see "Scaling further")
├── models/
│   └── score.py                 # Score ORM model (user_id, game_id, score, updated_at)
├── schemas/
│   ├── score.py                 # request/response models for score submission
│   └── leaderboard.py           # response models for ranking endpoints
├── routers/
│   └── leaderboard.py           # all HTTP routes
├── services/
│   └── leaderboard_service.py   # business rules
└── repositories/
    └── leaderboard_repository.py # SQL queries (including ranking window functions)
tests/
├── test_scores.py               # Submit Score tests
├── test_leaderboard.py          # Top X Rank tests
├── test_rank.py                 # User Context tests
└── conftest.py                  # test fixtures (in-memory SQLite + FastAPI TestClient)
```

`models/user.py` and `models/game.py` (and their `schemas/` counterparts) are placeholders — this service currently treats `user_id` and `game_id` as opaque identifiers owned by another service, rather than managing full user/game entities itself.

## Data model

A single table, `scores`, with a unique constraint on `(user_id, game_id)` — one row per user per game, holding their **highest** score for that game.

| column     | type      | notes                          |
|------------|-----------|---------------------------------|
| id         | integer   | primary key                     |
| user_id    | string    | indexed                         |
| game_id    | string    | indexed                         |
| score      | float     | the user's high score for the game |
| updated_at | datetime  | set on insert and update        |

## Key design decisions

- **Score submission keeps the highest score, not the latest.** A submission only overwrites the stored score if it's strictly greater. This matches classic arcade/high-score leaderboards (Pac-Man, mobile score-attack games) rather than an ELO-style rating or an accumulating XP total.
- **Ranking is per game, not global.** Each game has its own independent leaderboard; there's no cross-game aggregate score.
- **Ties share the same rank** (`1, 1, 3`, not `1, 2, 3`), computed with SQL's `RANK()` window function — the standard "competition ranking" behavior.
- **Ranking is computed live from SQL, not cached**, using `RANK()` and `ROW_NUMBER()` window functions over the full per-game population, so results are always consistent with the latest writes. This is simple and correct at moderate scale; see "Scaling further" for how this would change at very high read volume.
- **`limit`/`window` query params are capped server-side** (`limit` ≤ 100 on Top X, `window` ≤ 20 on User Context) to prevent unbounded queries.
- **User Context on an unknown user returns `200` with `null` rank/score and empty neighbor lists**, rather than a `404` — the caller asked "where does this user stand," and "nowhere yet" is a valid answer, not an error.
- **Neighbor ordering under ties is deterministic.** `RANK()` alone doesn't tell you who is "immediately above" a tied user, so the repository also computes `ROW_NUMBER()` over `(score DESC, user_id ASC)` to get a stable position for neighbor lookups, independent of the displayed (shared) rank.

## API reference

### `POST /scores`

Submit a score for a user in a game. Updates the stored score only if it's a new high score.

```json
// Request
{ "user_id": "u1", "game_id": "chess", "score": 150 }

// Response
{
  "user_id": "u1",
  "game_id": "chess",
  "score": 150,
  "updated_at": "2026-09-22T18:05:06",
  "is_new_high_score": true
}
```

### `GET /leaderboard/{game_id}/top?limit=10`

Top-ranked users for a game. `limit` defaults to 10, max 100.

```json
{
  "game_id": "chess",
  "entries": [
    { "rank": 1, "user_id": "u2", "score": 150, "updated_at": "2026-09-22T18:05:06" },
    { "rank": 2, "user_id": "u1", "score": 100, "updated_at": "2026-09-22T18:04:01" }
  ]
}
```

### `GET /leaderboard/{game_id}/users/{user_id}/context?window=2`

A user's rank plus their nearest neighbors. `window` defaults to 2, max 20.

```json
{
  "game_id": "chess",
  "user_id": "u3",
  "rank": 3,
  "score": 40,
  "above": [
    { "rank": 1, "user_id": "u5", "score": 60, "updated_at": "..." },
    { "rank": 2, "user_id": "u4", "score": 50, "updated_at": "..." }
  ],
  "below": [
    { "rank": 4, "user_id": "u2", "score": 30, "updated_at": "..." },
    { "rank": 5, "user_id": "u1", "score": 20, "updated_at": "..." }
  ]
}
```

### `GET /health`

Liveness check, returns `{"status": "ok"}`.

Interactive docs are available at `/docs` (Swagger UI) once the app is running.

## Getting started

### Requirements

- Python 3.11+
- (Optional) PostgreSQL, if you don't want to use the SQLite default

### Setup

```bash
git clone <repo-url>
cd LeaderBoard_Service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run

```bash
uvicorn app.main:app --reload
```

The app starts on `http://127.0.0.1:8000` by default. Visit `http://127.0.0.1:8000/docs` for interactive Swagger docs.

By default it uses a local SQLite file (`leaderboard.db`), created automatically on first run — no database setup needed to get started.

### Run tests

```bash
pip install pytest httpx
python -m pytest tests/ -v
```

Tests run against an isolated in-memory SQLite database (see `tests/conftest.py`), so they don't touch your local `leaderboard.db`.

## Configuration

Settings are read from environment variables (or a local `.env` file), defined in `app/config.py`:

| variable       | default                          | description                          |
|----------------|-----------------------------------|---------------------------------------|
| `DATABASE_URL` | `sqlite:///./leaderboard.db`      | SQLAlchemy connection string          |
| `APP_NAME`     | `Leaderboard Service`             | app display name                      |

To use Postgres instead of SQLite, set:

```bash
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
```

A `postgres://` URL (as some providers give you) is automatically normalized to `postgresql://`, which SQLAlchemy 2.x requires.

## Deployment (DigitalOcean App Platform)

1. Push this repo to GitHub and create a new App Platform app from it.
2. Add a managed PostgreSQL database component and bind its connection string to the app's `DATABASE_URL` environment variable.
3. App Platform detects `requirements.txt` and runs the app via the Python buildpack; the run command should be:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```
4. `psycopg2-binary` in `requirements.txt` provides the Postgres driver — without it, the app fails to import with `ModuleNotFoundError: No module named 'psycopg2'`.

## Scaling further

Current ranking queries hit SQL directly with window functions, which is correct and simple, but re-scans the per-game population on every read. At high read volume, the standard next step is to maintain a **Redis sorted set** per game (`ZADD`/`ZREVRANK`/`ZRANGE`) alongside Postgres — Postgres stays the durable source of truth, Redis serves live rank lookups in O(log N). `app/cache.py` is reserved for this.

def submit(client, user_id, game_id, score):
    return client.post("/scores", json={"user_id": user_id, "game_id": game_id, "score": score})


def test_top_scores_orders_by_score_descending(client):
    submit(client, "u1", "chess", 50)
    submit(client, "u2", "chess", 100)
    submit(client, "u3", "chess", 75)

    response = client.get("/leaderboard/chess/top")

    assert response.status_code == 200
    body = response.json()
    assert body["game_id"] == "chess"
    scores = [entry["score"] for entry in body["entries"]]
    assert scores == [100, 75, 50]


def test_top_scores_assigns_ranks_starting_at_one(client):
    submit(client, "u1", "chess", 50)
    submit(client, "u2", "chess", 100)

    response = client.get("/leaderboard/chess/top")

    entries = response.json()["entries"]
    assert entries[0]["rank"] == 1
    assert entries[0]["user_id"] == "u2"
    assert entries[1]["rank"] == 2
    assert entries[1]["user_id"] == "u1"


def test_tied_scores_share_the_same_rank(client):
    submit(client, "u1", "chess", 100)
    submit(client, "u2", "chess", 100)
    submit(client, "u3", "chess", 50)

    response = client.get("/leaderboard/chess/top")

    entries = response.json()["entries"]
    ranks = {entry["user_id"]: entry["rank"] for entry in entries}
    assert ranks["u1"] == 1
    assert ranks["u2"] == 1
    assert ranks["u3"] == 3


def test_limit_restricts_number_of_entries(client):
    for i in range(15):
        submit(client, f"u{i}", "chess", i)

    response = client.get("/leaderboard/chess/top?limit=5")

    assert len(response.json()["entries"]) == 5


def test_limit_defaults_to_ten(client):
    for i in range(15):
        submit(client, f"u{i}", "chess", i)

    response = client.get("/leaderboard/chess/top")

    assert len(response.json()["entries"]) == 10


def test_limit_above_max_is_rejected(client):
    response = client.get("/leaderboard/chess/top?limit=101")

    assert response.status_code == 422


def test_leaderboard_is_scoped_per_game(client):
    submit(client, "u1", "chess", 100)
    submit(client, "u1", "poker", 20)

    response = client.get("/leaderboard/poker/top")

    entries = response.json()["entries"]
    assert len(entries) == 1
    assert entries[0]["score"] == 20


def test_empty_leaderboard_returns_empty_list(client):
    response = client.get("/leaderboard/unknown-game/top")

    assert response.status_code == 200
    assert response.json()["entries"] == []

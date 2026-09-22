def submit(client, user_id, game_id, score):
    return client.post("/scores", json={"user_id": user_id, "game_id": game_id, "score": score})


def test_user_context_returns_rank_and_neighbors(client):
    for i, score in enumerate([10, 20, 30, 40, 50, 60]):
        submit(client, f"u{i}", "chess", score)

    response = client.get("/leaderboard/chess/users/u3/context")

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "u3"
    assert body["score"] == 40
    assert [e["user_id"] for e in body["above"]] == ["u5", "u4"]
    assert [e["user_id"] for e in body["below"]] == ["u2", "u1"]


def test_user_context_at_top_has_no_users_above(client):
    submit(client, "u1", "chess", 10)
    submit(client, "u2", "chess", 20)
    submit(client, "u3", "chess", 30)

    response = client.get("/leaderboard/chess/users/u3/context")

    body = response.json()
    assert body["above"] == []
    assert [e["user_id"] for e in body["below"]] == ["u2", "u1"]


def test_user_context_at_bottom_has_no_users_below(client):
    submit(client, "u1", "chess", 10)
    submit(client, "u2", "chess", 20)
    submit(client, "u3", "chess", 30)

    response = client.get("/leaderboard/chess/users/u1/context")

    body = response.json()
    assert body["below"] == []
    assert [e["user_id"] for e in body["above"]] == ["u3", "u2"]


def test_window_query_param_adjusts_neighbor_count(client):
    for i, score in enumerate([10, 20, 30, 40, 50]):
        submit(client, f"u{i}", "chess", score)

    response = client.get("/leaderboard/chess/users/u2/context?window=1")

    body = response.json()
    assert [e["user_id"] for e in body["above"]] == ["u3"]
    assert [e["user_id"] for e in body["below"]] == ["u1"]


def test_unknown_user_returns_200_with_null_context(client):
    submit(client, "u1", "chess", 10)

    response = client.get("/leaderboard/chess/users/ghost/context")

    assert response.status_code == 200
    body = response.json()
    assert body["rank"] is None
    assert body["score"] is None
    assert body["above"] == []
    assert body["below"] == []

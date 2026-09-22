def test_submit_score_creates_new_record(client):
    response = client.post("/scores", json={"user_id": "u1", "game_id": "chess", "score": 100})

    assert response.status_code == 200
    body = response.json()
    assert body["score"] == 100
    assert body["is_new_high_score"] is True


def test_submit_lower_score_does_not_overwrite_high_score(client):
    client.post("/scores", json={"user_id": "u1", "game_id": "chess", "score": 100})

    response = client.post("/scores", json={"user_id": "u1", "game_id": "chess", "score": 50})

    assert response.status_code == 200
    body = response.json()
    assert body["score"] == 100
    assert body["is_new_high_score"] is False


def test_submit_higher_score_overwrites_high_score(client):
    client.post("/scores", json={"user_id": "u1", "game_id": "chess", "score": 100})

    response = client.post("/scores", json={"user_id": "u1", "game_id": "chess", "score": 150})

    assert response.status_code == 200
    body = response.json()
    assert body["score"] == 150
    assert body["is_new_high_score"] is True


def test_same_user_different_games_are_tracked_independently(client):
    client.post("/scores", json={"user_id": "u1", "game_id": "chess", "score": 100})

    response = client.post("/scores", json={"user_id": "u1", "game_id": "poker", "score": 10})

    assert response.status_code == 200
    body = response.json()
    assert body["game_id"] == "poker"
    assert body["score"] == 10


def test_negative_score_is_rejected(client):
    response = client.post("/scores", json={"user_id": "u1", "game_id": "chess", "score": -5})

    assert response.status_code == 422


def test_missing_fields_are_rejected(client):
    response = client.post("/scores", json={"user_id": "u1", "score": 5})

    assert response.status_code == 422

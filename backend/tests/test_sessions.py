import pytest


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_create_and_get_session(client):
    created = client.post("/api/sessions", json={"mode": "chat"}).json()
    assert created["mode"] == "chat"
    assert created["messages"] == []

    fetched = client.get(f"/api/sessions/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]


def test_get_unknown_session_returns_404(client):
    assert client.get("/api/sessions/does-not-exist").status_code == 404


def test_list_sessions_newest_first(client):
    first = client.post("/api/sessions", json={"mode": "chat"}).json()["id"]
    second = client.post("/api/sessions", json={"mode": "pdf"}).json()["id"]
    client.post("/api/chat", json={"message": "hi", "chat_session_id": first})

    ids = [s["id"] for s in client.get("/api/sessions").json()]
    assert ids == [first, second]


def test_delete_session(client):
    sid = client.post("/api/sessions", json={"mode": "chat"}).json()["id"]
    assert client.delete(f"/api/sessions/{sid}").status_code == 200
    assert client.get(f"/api/sessions/{sid}").status_code == 404


@pytest.mark.xfail(strict=True, reason="F4: fixed in fix/session-ownership")
def test_delete_unknown_session_returns_404(client):
    assert client.delete("/api/sessions/does-not-exist").status_code == 404


@pytest.mark.xfail(strict=True, reason="F4: fixed in fix/session-ownership")
def test_list_reports_message_count(client):
    sid = client.post("/api/sessions", json={"mode": "chat"}).json()["id"]
    client.post("/api/chat", json={"message": "hi", "chat_session_id": sid})
    assert client.get("/api/sessions").json()[0]["message_count"] == 2


@pytest.mark.xfail(strict=True, reason="S1: fixed in fix/session-ownership")
def test_sessions_are_private_to_their_owner(client):
    client.post("/api/sessions", json={"mode": "chat"}, headers={"X-Client-Id": "a" * 32})
    assert client.get("/api/sessions", headers={"X-Client-Id": "b" * 32}).json() == []

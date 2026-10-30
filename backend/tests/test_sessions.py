import pytest

from tests.conftest import STRANGER


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_health_db_runs_a_query_without_a_client_id(client, supabase):
    res = client.get("/health/db", headers={"X-Client-Id": ""})
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "database": "ok"}


def test_health_db_reports_503_without_leaking_details(client, monkeypatch):
    import core.storage

    def broken():
        raise RuntimeError("Unregistered API key sb_secret_xyz")
    monkeypatch.setattr(core.storage, "_get_client", broken)
    res = client.get("/health/db")
    assert res.status_code == 503
    assert res.json() == {"status": "error", "database": "unreachable"}


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


def test_delete_unknown_session_returns_404(client):
    assert client.delete("/api/sessions/does-not-exist").status_code == 404


def test_list_reports_message_count(client):
    sid = client.post("/api/sessions", json={"mode": "chat"}).json()["id"]
    client.post("/api/chat", json={"message": "hi", "chat_session_id": sid})
    assert client.get("/api/sessions").json()[0]["message_count"] == 2


def test_sessions_are_private_to_their_owner(client):
    client.post("/api/sessions", json={"mode": "chat"}, headers={"X-Client-Id": "a" * 32})
    assert client.get("/api/sessions", headers={"X-Client-Id": "b" * 32}).json() == []


@pytest.mark.parametrize("headers", [{"X-Client-Id": ""}, {"X-Client-Id": "short"}, {"X-Client-Id": "bad id!" * 4}])
def test_missing_or_malformed_client_id_is_rejected(client, headers):
    assert client.get("/api/sessions", headers=headers).status_code == 400


def test_stranger_gets_404_not_403(client):
    """Someone else's session looks exactly like one that does not exist."""
    sid = client.post("/api/sessions", json={"mode": "chat"}).json()["id"]
    assert client.get(f"/api/sessions/{sid}", headers=STRANGER).status_code == 404
    assert client.delete(f"/api/sessions/{sid}", headers=STRANGER).status_code == 404
    assert client.get(f"/api/sessions/{sid}").status_code == 200


def test_stored_owner_id_cannot_be_replayed_as_a_client_id(client, supabase):
    """Someone who reads owner_id out of the database still cannot act as that owner."""
    sid = client.post("/api/sessions", json={"mode": "chat"}).json()["id"]
    leaked = {"X-Client-Id": supabase.db["sessions"][0]["owner_id"]}
    assert client.get(f"/api/sessions/{sid}", headers=leaked).status_code == 404
    assert client.get("/api/sessions", headers=leaked).json() == []


def test_stranger_cannot_write_into_someone_elses_chat(client, gemini):
    sid = client.post("/api/sessions", json={"mode": "chat"}).json()["id"]
    res = client.post("/api/chat", headers=STRANGER, json={"message": "hi", "chat_session_id": sid})
    assert res.status_code == 404
    assert gemini.prompts == []  # rejected before spending model quota
    assert client.get(f"/api/sessions/{sid}").json()["messages"] == []

from google.api_core.exceptions import ResourceExhausted


def test_chat_returns_reply(client, gemini):
    res = client.post("/api/chat", json={"message": "Hello"})
    assert res.status_code == 200
    assert res.json()["reply"] == gemini.answer


def test_chat_sends_history_to_model(client, gemini):
    history = [
        {"role": "user", "content": "My codename is Quillfeather."},
        {"role": "assistant", "content": "Noted."},
    ]
    client.post("/api/chat", json={"message": "What is my codename?", "history": history})
    prompt = gemini.prompts[-1]
    assert "Quillfeather" in prompt
    assert prompt.rstrip().endswith("Assistant:")


def test_chat_persists_turn_and_titles_session(client):
    sid = client.post("/api/sessions", json={"mode": "chat"}).json()["id"]
    client.post("/api/chat", json={"message": "Tell me about orchards", "chat_session_id": sid})

    session = client.get(f"/api/sessions/{sid}").json()
    assert [m["role"] for m in session["messages"]] == ["user", "assistant"]
    assert session["title"] == "Tell me about orchards"


def test_chat_model_failure_returns_502(client, gemini):
    gemini.error = RuntimeError("upstream exploded")
    res = client.post("/api/chat", json={"message": "Hello"})
    assert res.status_code == 502
    assert res.json()["type"] == "LLMError"


def test_chat_rejects_empty_message(client):
    assert client.post("/api/chat", json={"message": ""}).status_code == 422


def test_quota_error_returns_429(client, gemini):
    gemini.error = ResourceExhausted("You exceeded your current quota")
    assert client.post("/api/chat", json={"message": "Hello"}).status_code == 429

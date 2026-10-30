"""S2: CORS limited to the configured origins. L4: unhandled 500s keep CORS headers."""
import pytest

from config.settings import Settings

FRONTEND = {"Origin": "http://localhost:5173"}  # the default ALLOWED_ORIGINS
ELSEWHERE = {"Origin": "https://evil.example"}


def test_allowed_origin_gets_cors_headers(client):
    res = client.get("/api/sessions", headers=FRONTEND)
    assert res.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_other_origins_get_no_cors_headers(client):
    res = client.get("/api/sessions", headers=ELSEWHERE)
    assert "access-control-allow-origin" not in res.headers


def test_preflight_from_another_origin_is_refused(client):
    res = client.options("/api/chat", headers={**ELSEWHERE, "Access-Control-Request-Method": "POST"})
    assert res.status_code == 400


def test_unhandled_error_is_a_readable_500_with_cors_headers(client, monkeypatch):
    import routers.sessions

    def boom(_owner):
        raise RuntimeError("secret internal detail")
    monkeypatch.setattr(routers.sessions, "list_sessions", boom)

    res = client.get("/api/sessions", headers=FRONTEND)
    assert res.status_code == 500
    assert res.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert res.json() == {"error": "An unexpected error occurred. Please try again.", "type": "InternalServerError"}
    assert "secret" not in res.text


def test_unhandled_error_still_writes_the_request_exit_log_line(client, monkeypatch, caplog):
    import routers.sessions
    monkeypatch.setattr(routers.sessions, "list_sessions", lambda _owner: 1 / 0)
    with caplog.at_level("INFO", logger="visionaryx.main"):
        client.get("/api/sessions")
    assert any("<-- GET /api/sessions | status=500" in r.message for r in caplog.records)


@pytest.mark.parametrize("raw, expected", [
    ("https://visionaryx-dusky.vercel.app/, http://localhost:5173",
     ["https://visionaryx-dusky.vercel.app", "http://localhost:5173"]),
    ("", []),
    (" , ", []),
])
def test_origin_list_ignores_blanks_and_trailing_slashes(raw, expected):
    s = Settings(google_api_key="x", huggingfacehub_api_token="x", allowed_origins=raw)
    assert s.origins_list == expected

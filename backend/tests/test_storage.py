import pytest

from core import storage

LEGACY_JWT = "eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.c2lnbmF0dXJl"
NEW_SECRET = "sb_secret_0123456789abcdefABCDEF"


@pytest.fixture
def supabase_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")

    def use(key):
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", key)
        return storage._get_client().session

    return use


def test_new_secret_key_goes_in_apikey_header_only(supabase_env):
    session = supabase_env(NEW_SECRET)
    assert session.headers["apikey"] == NEW_SECRET
    assert "Authorization" not in session.headers


def test_legacy_jwt_key_keeps_bearer_header(supabase_env):
    session = supabase_env(LEGACY_JWT)
    assert session.headers["apikey"] == LEGACY_JWT
    assert session.headers["Authorization"] == f"Bearer {LEGACY_JWT}"


def test_client_targets_the_rest_endpoint(supabase_env):
    assert str(supabase_env(NEW_SECRET).base_url).rstrip("/") == "https://example.supabase.co/rest/v1"

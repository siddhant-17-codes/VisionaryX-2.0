import pytest

from config.settings import Settings
from core import storage

LEGACY_JWT = "eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.c2lnbmF0dXJl"
NEW_SECRET = "sb_secret_0123456789abcdefABCDEF"


def settings(url="https://example.supabase.co", key=NEW_SECRET):
    return Settings(google_api_key="x", huggingfacehub_api_token="x", supabase_url=url, supabase_service_key=key)


@pytest.fixture
def supabase_env(monkeypatch):
    def use(key):
        monkeypatch.setattr(storage, "get_settings", lambda: settings(key=key))
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


def test_supabase_config_comes_from_settings_not_os_environ(monkeypatch):
    # Q2: Settings also reads backend/.env; os.environ does not, so a plain
    # `uvicorn main:app` used to fail every session call with KeyError.
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    monkeypatch.setattr(storage, "get_settings", lambda: settings())
    assert storage._get_client().session.headers["apikey"] == NEW_SECRET


@pytest.mark.parametrize("url,key", [("", NEW_SECRET), ("https://example.supabase.co", "")])
def test_missing_supabase_config_names_the_variables(monkeypatch, url, key):
    monkeypatch.setattr(storage, "get_settings", lambda: settings(url=url, key=key))
    with pytest.raises(RuntimeError, match="SUPABASE_URL and SUPABASE_SERVICE_KEY"):
        storage._get_client()


def test_client_is_reused_and_has_a_timeout(monkeypatch):
    monkeypatch.setattr(storage, "get_settings", lambda: settings())
    first, second = storage._get_client(), storage._get_client()
    assert first is second
    assert first.session.timeout.read == storage.SUPABASE_TIMEOUT


def test_timestamps_are_utc_and_still_sort_after_older_naive_rows():
    from datetime import UTC, datetime, timedelta
    older_naive_row = (datetime.now(UTC) - timedelta(seconds=1)).replace(tzinfo=None).isoformat()
    now = storage._now()
    assert now.endswith("+00:00") and len(now) == len("2026-10-30T21:00:00.000000+00:00")
    assert older_naive_row < now

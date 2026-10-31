"""How FAISS indexes are stored in Supabase's faiss_indexes.index_b64 column.

New rows hold the codec's JSON as plain text (one encoding). Rows written by 2.0.0
(base64 of the JSON) and before it (base64 of a legacy pickle) must still load,
the legacy ones only as data."""
import base64

import pytest

from core import faiss_codec, storage
from tests.test_faiss_codec import EMB, assert_same, legacy_blob, store

SESSION, OWNER = "pdf-session-1", "a" * 64


def stored_value(supabase) -> str:
    return supabase.db["faiss_indexes"][0]["index_b64"]


def put_row(supabase, value: str):
    supabase.table("faiss_indexes").upsert(
        {"session_id": SESSION, "owner_id": OWNER, "index_b64": value, "updated_at": "x"}).execute()


def test_new_index_is_stored_as_plain_json_text_and_round_trips(supabase):
    original = store()
    data = faiss_codec.dumps(original)
    storage.save_faiss_index(SESSION, OWNER, data)

    value = stored_value(supabase)
    assert value.startswith('{"format": "visionaryx-faiss/1"')  # no extra base64 layer
    assert len(value.encode()) == len(data)  # base64 would have added a third
    loaded = storage.load_faiss_index(SESSION, OWNER)
    assert loaded == data
    assert_same(original, faiss_codec.loads(loaded, EMB))


def test_index_written_by_2_0_0_as_base64_json_still_loads(supabase):
    original = store()
    put_row(supabase, base64.b64encode(faiss_codec.dumps(original)).decode())
    assert_same(original, faiss_codec.loads(storage.load_faiss_index(SESSION, OWNER), EMB))


def test_legacy_pickled_index_still_loads_as_data(supabase):
    original = store()
    put_row(supabase, base64.b64encode(legacy_blob(original)).decode())
    assert_same(original, faiss_codec.loads(storage.load_faiss_index(SESSION, OWNER), EMB))


def test_index_is_scoped_to_its_owner(supabase):
    storage.save_faiss_index(SESSION, OWNER, faiss_codec.dumps(store()))
    assert storage.load_faiss_index(SESSION, "b" * 64) is None


def test_saving_anything_but_the_codec_json_is_refused(supabase):
    with pytest.raises(ValueError):
        storage.save_faiss_index(SESSION, OWNER, b"\x80\x04 not json")

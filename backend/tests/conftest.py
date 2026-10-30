"""Shared fixtures. Every external service (Supabase, Gemini, Gemini embeddings,
Hugging Face) is replaced with an in-memory fake, so tests never touch the network
or spend API quota. Dummy keys are set before the app is imported."""
import copy
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

for _key in ("GOOGLE_API_KEY", "HUGGINGFACEHUB_API_TOKEN", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"):
    os.environ[_key] = "test-dummy"

from fastapi.testclient import TestClient  # noqa: E402
from langchain_core.embeddings import DeterministicFakeEmbedding  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
PRIMARY_KEYS = {"sessions": "id", "faiss_indexes": "session_id"}


# ── Supabase ─────────────────────────────────────────────────────────────────

class FakeQuery:
    def __init__(self, db: dict, table: str):
        self.rows = db.setdefault(table, [])
        self.pk = PRIMARY_KEYS.get(table, "id")
        self.op, self.payload, self.cols, self.order_by = "select", None, "*", None
        self.filters: list[tuple[str, object]] = []

    def select(self, cols="*"):
        self.op, self.cols = "select", cols
        return self

    def insert(self, row):
        self.op, self.payload = "insert", row
        return self

    def upsert(self, row):
        self.op, self.payload = "upsert", row
        return self

    def update(self, values):
        self.op, self.payload = "update", values
        return self

    def delete(self):
        self.op = "delete"
        return self

    def eq(self, col, value):
        self.filters.append((col, value))
        return self

    def order(self, col, desc=False):
        self.order_by = (col, desc)
        return self

    def execute(self):
        matched = [r for r in self.rows if all(r.get(c) == v for c, v in self.filters)]
        if self.op == "select":
            out = copy.deepcopy(matched)
            if self.order_by:
                out.sort(key=lambda r: r[self.order_by[0]], reverse=self.order_by[1])
            if self.cols != "*":
                keep = [c.strip() for c in self.cols.split(",")]
                out = [{k: r.get(k) for k in keep} for r in out]
            return SimpleNamespace(data=out)
        if self.op == "insert":
            self.rows.append(copy.deepcopy(self.payload))
            return SimpleNamespace(data=[self.payload])
        if self.op == "upsert":
            self.rows[:] = [r for r in self.rows if r.get(self.pk) != self.payload[self.pk]]
            self.rows.append(copy.deepcopy(self.payload))
            return SimpleNamespace(data=[self.payload])
        if self.op == "update":
            for r in matched:
                r.update(copy.deepcopy(self.payload))
            return SimpleNamespace(data=matched)
        if self.op == "delete":
            self.rows[:] = [r for r in self.rows if r not in matched]
            return SimpleNamespace(data=matched)
        raise AssertionError(f"unsupported op {self.op}")


class FakeSupabase:
    def __init__(self):
        self.db: dict[str, list[dict]] = {}

    def table(self, name):
        return FakeQuery(self.db, name)


# ── Gemini ───────────────────────────────────────────────────────────────────

class FakeGemini:
    """Stands in for the GenerativeModel. Records every prompt it receives."""

    def __init__(self):
        self.prompts: list = []
        self.error: Exception | None = None
        self.answer = "Fake answer from the model."

    def generate_content(self, prompt):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        if isinstance(prompt, str) and "3 questions:" in prompt:
            return SimpleNamespace(text="What is A?\nWhat is B?\nWhat is C?")
        return SimpleNamespace(text=self.answer)


# ── Hugging Face ─────────────────────────────────────────────────────────────

class FakeInferenceClient:
    error: Exception | None = None

    def __init__(self, *args, **kwargs):
        pass

    def text_to_image(self, prompt, model=None):
        if FakeInferenceClient.error:
            raise FakeInferenceClient.error
        from PIL import Image
        return Image.new("RGB", (1024, 1024), "orange")


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def supabase(monkeypatch):
    fake = FakeSupabase()
    import core.storage
    monkeypatch.setattr(core.storage, "_get_client", lambda: fake)
    return fake


@pytest.fixture
def gemini(monkeypatch):
    fake = FakeGemini()
    import services.gemini_service
    monkeypatch.setattr(services.gemini_service, "_model", fake)
    return fake


@pytest.fixture(autouse=True)
def fake_embeddings(monkeypatch):
    import core.embeddings
    monkeypatch.setattr(core.embeddings, "get_embeddings", lambda: DeterministicFakeEmbedding(size=64))


@pytest.fixture
def hf(monkeypatch):
    import services.image_service
    FakeInferenceClient.error = None
    monkeypatch.setattr(services.image_service, "InferenceClient", FakeInferenceClient)
    return FakeInferenceClient


OWNER = "owner" + "0" * 27
STRANGER = {"X-Client-Id": "stranger" + "0" * 24}


@pytest.fixture
def client(supabase, gemini, hf):
    """Every request carries OWNER's X-Client-Id unless a test overrides the header."""
    from main import app
    return TestClient(app, raise_server_exceptions=False, headers={"X-Client-Id": OWNER})


def fixture_bytes(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


@pytest.fixture
def uploaded_pdf(client):
    """A chat session with the fictional Lumen Ridge report indexed."""
    chat_id = client.post("/api/sessions", json={"mode": "pdf"}).json()["id"]
    res = client.post(
        "/api/pdf/upload",
        files=[("files", ("lumen_ridge_report.pdf", fixture_bytes("lumen_ridge_report.pdf"), "application/pdf"))],
        data={"chat_session_id": chat_id},
    )
    assert res.status_code == 200, res.text
    return SimpleNamespace(chat_id=chat_id, **res.json())

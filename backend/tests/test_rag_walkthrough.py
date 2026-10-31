"""scripts/rag_walkthrough.py: a clear failure without a key, and a full offline run
on the example files with the shared fakes (no network, no quota)."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "rag_walkthrough.py"
EXAMPLES = REPO / "examples"
QUESTION = "When will the new cold-storage building open, and what will it cost?"


def test_missing_key_exits_with_a_clear_message():
    env = {**os.environ, "GOOGLE_API_KEY": ""}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(EXAMPLES / "lumen_ridge_annual_report_2025.pdf"), "-q", "x"],
        capture_output=True, text=True, env=env, timeout=120,
    )
    assert result.returncode == 2
    assert "GOOGLE_API_KEY is not set" in result.stderr


def test_runs_every_stage_offline(monkeypatch, tmp_path, gemini, capsys):
    monkeypatch.chdir(tmp_path)  # the script changes directory; restore it afterwards
    spec = importlib.util.spec_from_file_location("rag_walkthrough", SCRIPT)
    walkthrough = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(walkthrough)
    out = tmp_path / "run.json"
    monkeypatch.setattr(sys, "argv", ["rag_walkthrough.py",
                                      str(EXAMPLES / "lumen_ridge_annual_report_2025.pdf"),
                                      str(EXAMPLES / "lumen_ridge_cold_storage_plan.docx"),
                                      "-q", QUESTION, "--json", str(out)])
    walkthrough.main()

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["index"]["class"] == "IndexFlatL2"
    assert report["embedding"]["shape"] == [len(report["chunks"]), 64]  # the fake's size
    assert len(report["retrieval"]["results"]) == 5
    assert report["citations"], "at least one citation"
    assert report["answer"]["model"] == "fake-primary"
    assert "=== 6. Answer" in capsys.readouterr().out

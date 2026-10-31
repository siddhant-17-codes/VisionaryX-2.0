# Documentation

Start with the [project README](../README.md) for what VisionaryX does and how to run it.

| Document | What it covers |
|---|---|
| [RAG_DEEP_DIVE.md](RAG_DEEP_DIVE.md) | Retrieval-augmented generation taught through this codebase: extraction, chunking, embeddings, FAISS search, the adaptive threshold, prompt assembly, citations and storage, with a worked example on real numbers and a glossary |
| [ARCHITECTURE.md](ARCHITECTURE.md) | What runs where, the request lifecycle of each feature, the deployment, and the security model |
| [releases/v2.0.0.md](releases/v2.0.0.md) | Release notes for 2.0.0, the October 2026 revival |
| [../SECURITY.md](../SECURITY.md) | Reporting a vulnerability, how secrets are handled, and what data is stored |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Setup, tests, branch and commit style, CI |
| [../scripts/demo/README.md](../scripts/demo/README.md) | How the demo video and screenshots are recorded and cut |
| [../examples/README.md](../examples/README.md) | The fictional files to try the app with |

Other files here:

- [`assets/`](assets/): the demo GIF and screenshots used in the README.
- `VisionaryX_visuals.html`: an early design mock-up of the interface, made before the
  2026 revival. Some of its text (such as "sessions saved to
  disk" and the fixed "Gemini 2.5" labels) no longer matches the app.

Helper scripts:

- [`scripts/rag_walkthrough.py`](../scripts/rag_walkthrough.py): runs the RAG pipeline on
  local files and prints every stage (see
  [Try it yourself](RAG_DEEP_DIVE.md#try-it-yourself)).
- [`scripts/checks/mobile_layout_check.py`](../scripts/checks/mobile_layout_check.py):
  checks the phone layout against a local build with a mocked API.

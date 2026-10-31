# Contributing

Thanks for your interest. VisionaryX is a personal learning project, so issues and pull
requests are welcome but reviewed by one person; small, focused changes are the easiest
to accept. Security problems: see [SECURITY.md](SECURITY.md) instead of opening an issue.

## Set up

Follow [Run it locally](README.md#run-it-locally) in the README: Python 3.12 for
`backend/`, Node.js 20 or later for `frontend/`, and a free Supabase project created
from `supabase/schema.sql`. You only need real keys to run the app; the tests need none.

## Tests and lint

```bash
cd backend
pytest                                    # every external service is faked
ruff check .                              # the backend
ruff check --config pyproject.toml ../scripts   # the helper scripts, as CI does

cd ../frontend
npm test                                  # Vitest + Testing Library
npm run lint                              # ESLint
npm run build                             # the production build CI runs
```

Or, with GNU make and a POSIX shell, `make test` and `make lint` from the root.

Tests must never need a network or a key: use the fixtures in `backend/tests/conftest.py`
(`client`, `supabase`, `gemini`, `use_chain`, `hf`; embeddings are faked for every test).
A test that reaches a real service is a bug.

## How changes are made

- **One branch per area**, named by kind: `fix/…`, `feat/…`, `refactor/…`, `chore/…`,
  `docs/…`, `test/…`. Keep backend and frontend changes apart where you can.
- **Bugs start as failing tests.** Write a test that shows the bug before fixing it. If
  the fix belongs in a later branch, mark the test
  `@pytest.mark.xfail(strict=True, reason="…: fixed in fix/your-branch")` (or `it.fails`
  in Vitest); being strict, it turns red once the bug is fixed, and the fixing branch
  removes the marker.
- **Commit messages** follow the existing history: a short imperative subject with a type
  and optional scope, such as `fix(backend): …`, `feat(frontend): …`, `docs: …`,
  `chore: …`, `test(backend): …`; then a body that says what changed and why, and what it
  means for someone using the site.
- **Pull requests** say what changes for users, how it was tested, and anything a deploy
  needs (a new environment variable, a SQL migration).
- **CI must be green** before a merge. `.github/workflows/ci.yml` runs on every push and
  pull request: *Backend (ruff + pytest)* and *Frontend (eslint + vitest + build)*.
  Branches are merged into `main` with a merge commit.
- **Dependencies:** see [Dependency policy](#dependency-policy) below.
- **Never commit** `.env` files, keys, or personal files; `.gitignore` covers the usual
  ones.

## Dependency policy

- **Backend:** direct dependencies are pinned in `backend/requirements.in`; the full tree is
  locked in `backend/requirements.txt` with `make -C backend lock`
  (`uv pip compile requirements.in --universal --python-version 3.12`). The `--universal`
  flag keeps platform markers, such as `uvloop` only off Windows and `colorama` only on it,
  so the same lock installs on Linux (CI, Render) and Windows.
- **Frontend:** `frontend/package.json` and `package-lock.json`, through `npm`.
- **Dependabot** (`.github/dependabot.yml`) opens one grouped pull request a week per
  ecosystem (pip, npm, GitHub Actions) for minor and patch updates, and ignores
  semver-major updates. FastAPI is kept out of the pip group: it is 0.x, so its "minor"
  releases can break, and recent ones require Starlette 1.x.
- **Dependabot's pip lock files need regenerating.** Its pip pull requests rewrite
  `requirements.txt` without uv's `--universal` markers (seen in October 2026: `uvloop`
  became unconditional, which cannot install on Windows, and `colorama` was dropped).
  Apply the versions with `make -C backend lock` in a normal branch instead, run the tests,
  and close the Dependabot pull request as superseded.
- **Every update** must pass CI; backend updates also run the FAISS codec and index storage
  tests (`tests/test_faiss_codec.py`, `tests/test_index_storage.py`), and after a backend
  merge Render's `/health` and `/health/db` are checked.
- **Accepted risk:** `npm audit` reports moderate advisories in ESLint's dependencies
  (dev-only lint tooling, never shipped to the browser). The only fix npm offers is a
  downgrade to ESLint 4, so they are accepted.

### Planned major upgrades

Major versions are upgraded deliberately, one at a time, each on its own branch with a
migration and tests. Open as of 2026-10-31:

| Package | Current → available | Why it matters | Risk |
|---|---|---|---|
| FastAPI (with Starlette) | 0.115.6 → 0.162.0 (Starlette 0.41.3 → 1.10.0) | Stay on supported releases and receive fixes | Starlette 1.0 removes deprecated APIs; the app's middleware, error handlers and `TestClient` use need checking |
| pypdf | 4.3.1 → 6.x | Newer releases fix many parsing problems with malformed PDFs | Two majors of API changes; all three extraction strategies (standard, layout, visitor) and the scanned-PDF refusal need re-testing on real files |
| React + react-dom | 18.3.1 → 19.x | Current React; the ecosystem is moving to it | Changes to refs and rendering; react-markdown, react-router and Testing Library must be checked together |
| react-markdown | 9.1.0 → 10.x | Keep the markdown renderer current | Breaking API changes in 10.0 (check the changelog); answers' code blocks and numbered lists are pinned by `ChatBubble.test.jsx` |
| Vite | 6.4.5 → 8.x | Faster builds; Vite 6 will leave support | Newer Node requirement; `@vitejs/plugin-react` and Vitest must move with it |

## Deploys

`main` deploys the frontend to Vercel and the backend to Render automatically, on every
merge. After a merge that touches `backend/`, check that `/health` and `/health/db` return
200 before merging anything else.

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
- **Dependencies:** edit `backend/requirements.in`, then regenerate the lock with
  `make -C backend lock` (needs `uv`); frontend dependencies go through `npm`. Dependabot
  opens weekly update pull requests, which the maintainer reviews by hand.
- **Never commit** `.env` files, keys, or personal files; `.gitignore` covers the usual
  ones.

## Deploys

`main` deploys the frontend to Vercel automatically. The backend on Render is deployed by
hand, so a backend change is not live until the maintainer deploys it.

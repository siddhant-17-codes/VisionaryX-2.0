# Security

## Reporting a vulnerability

Please report security problems privately, not in a public issue: use GitHub's
**Report a vulnerability** button on the repository's
[Security tab](https://github.com/siddhant-17-codes/VisionaryX-2.0/security), or message
the maintainer on [LinkedIn](https://www.linkedin.com/in/siddhantthakur-/) to arrange a
private channel. Include what you found, how to reproduce it, and what it exposes.

This is a personal project maintained by one person, so a reply may take a few days.
Please do not test against the live site in ways that affect other visitors (no
load testing, no attempts to read other people's conversations, no automated scanning that
uses up the shared free quotas). A local copy (see the [README](README.md#run-it-locally))
is the right place for that.

## Supported versions

Only the latest code on `main` (currently release 2.0.1) receives fixes.

## Secret handling

- The backend's keys (Gemini, Supabase service key, Cloudflare, Hugging Face) exist only
  in Render's environment settings and, for local development, in `backend/.env`, which
  is gitignored. `backend/.env.example` lists the names with placeholder values.
- The frontend holds no secrets. Its only setting, `VITE_API_URL`, is public.
- The Supabase **service** key bypasses row-level security and must never be used in a
  browser. The public (anon/publishable) keys can read nothing, because RLS is on with no
  policies.
- The test suite never reads `backend/.env`: it sets dummy keys and fakes every external
  service, and fails any test that tries to reach the real Cloudflare API.
- The demo recorder (`scripts/demo/record-demo.mjs`) checks every API response and the
  final page text for the key values in `backend/.env` and fails if one appears.
- If a key is ever exposed, rotate it at the provider first, then update Render. Rotation
  was used in October 2026 to cut off an old deployment that still held the keys.

## What is stored

There are no accounts, and no names or e-mail addresses are collected.

| Data | Where | Kept until |
|---|---|---|
| Your conversations in General Chat and PDF Chat: questions, answers, which model answered, a title (the first 50 characters of the first question, or the first file name), timestamps | Supabase, table `sessions` | You delete the chat |
| Uploaded documents' file names, and their text split into chunks with page or section labels and embedding vectors | Supabase, table `faiss_indexes` | You delete the PDF chat |
| The SHA-256 hash of your browser's anonymous ID (`owner_id`), on both tables | Supabase | With the rows above |
| Your browser's anonymous ID itself | Your browser's `localStorage` (`vx_client_id`) | You clear site data |
| Request log lines: path, status, duration; for PDF questions and image prompts their first 60 characters; uploaded file names | Render's logs | Render's log retention |
| Per-IP request timestamps for rate limiting | Backend memory | At most 24 hours, and lost on every restart |

**Not stored:** the original uploaded files, images sent to Image Query, generated images,
your raw anonymous ID, and IP addresses (except in memory for rate limiting, and whatever
Render and Cloudflare log as infrastructure providers).

**Sent to third parties to answer you:** questions, document chunks and images go to
Google's Gemini API; image prompts go to Cloudflare Workers AI (or Hugging Face if
Cloudflare fails). The app uses Gemini's free tier; Google's terms for unpaid use allow it
to use submitted content to improve its products, so do not upload confidential documents.

**Not yet in place:** automatic expiry. Data stays until the chat is deleted.

How visitors' data is kept apart is described under
[Security model](docs/ARCHITECTURE.md#security-model).

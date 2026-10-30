-- fix/session-ownership
-- Tie every chat session and FAISS index to the anonymous browser that created it
-- (the X-Client-Id header). Run once in the Supabase SQL editor BEFORE deploying the
-- backend from this branch.
--
-- Additive only: no existing row is changed or deleted. Rows created before this
-- migration keep owner_id = NULL, which the new backend never matches, so they stop
-- showing up in the app but stay in the database.
-- Safe to re-run.

begin;

alter table public.sessions      add column if not exists owner_id text;
alter table public.faiss_indexes add column if not exists owner_id text;

-- GET /api/sessions filters by owner and sorts by updated_at.
create index if not exists sessions_owner_updated_idx
    on public.sessions (owner_id, updated_at desc);

commit;

-- Verify (expect two rows, both data_type = text):
-- select table_name, column_name, data_type
--   from information_schema.columns
--  where table_schema = 'public'
--    and table_name in ('sessions', 'faiss_indexes')
--    and column_name = 'owner_id';

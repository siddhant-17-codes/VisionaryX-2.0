-- fix/session-ownership
-- Run in the Supabase SQL editor BEFORE deploying the backend from this branch.
--
-- The editor only shows the result of the LAST statement it runs, so run the
-- sections one at a time: highlight a section and press Run (Ctrl+Enter runs the
-- selection).

-- ═════════════════════════════════════════════════════════════════════════════
-- SECTION 1: owner columns (additive, safe to re-run)
-- Ties every chat session and FAISS index to the browser that created it. The
-- backend stores SHA-256(X-Client-Id) here, never the raw id.
-- ═════════════════════════════════════════════════════════════════════════════

begin;

alter table public.sessions      add column if not exists owner_id text;
alter table public.faiss_indexes add column if not exists owner_id text;

-- GET /api/sessions filters by owner and sorts by updated_at.
create index if not exists sessions_owner_updated_idx
    on public.sessions (owner_id, updated_at desc);

commit;

-- Check (expect two rows, both data_type = text):
select table_name, column_name, data_type
  from information_schema.columns
 where table_schema = 'public'
   and table_name in ('sessions', 'faiss_indexes')
   and column_name = 'owner_id';


-- ═════════════════════════════════════════════════════════════════════════════
-- SECTION 2: DATA CLEANUP. DELETES ROWS. CANNOT BE UNDONE.
-- Approved by the owner on 2026-10-30. Removes every session and FAISS index
-- with no owner: everything created before this migration, including the
-- third-party résumé and the audit test leftovers. The new backend never shows
-- these rows, so nothing visible to users changes.
-- ═════════════════════════════════════════════════════════════════════════════

-- 2a. Preview: run this ALONE first and note the counts.
select 'sessions' as table_name, count(*) as rows_to_delete
  from public.sessions where owner_id is null
union all
select 'faiss_indexes', count(*)
  from public.faiss_indexes where owner_id is null;

-- 2b. Delete: the result shows how many rows went; it should match 2a.
with deleted_sessions as (
    delete from public.sessions where owner_id is null returning 1
), deleted_indexes as (
    delete from public.faiss_indexes where owner_id is null returning 1
)
select (select count(*) from deleted_sessions) as sessions_deleted,
       (select count(*) from deleted_indexes)  as faiss_indexes_deleted;


-- ═════════════════════════════════════════════════════════════════════════════
-- SECTION 3: ROW LEVEL SECURITY (safe to re-run)
-- RLS on, no policies: the anon and authenticated roles (the public keys) can
-- no longer read or write these tables at all. The backend is unaffected: its
-- secret / service_role key runs as the service_role Postgres role, which has
-- BYPASSRLS. RLS does NOT stop anyone holding that key; key rotation does.
-- ═════════════════════════════════════════════════════════════════════════════

alter table public.sessions      enable row level security;
alter table public.faiss_indexes enable row level security;

-- Check (expect rls_enabled = true and policies = 0 for both):
select c.relname as table_name,
       c.relrowsecurity as rls_enabled,
       (select count(*) from pg_policies p
         where p.schemaname = 'public' and p.tablename = c.relname) as policies
  from pg_class c
  join pg_namespace n on n.oid = c.relnamespace
 where n.nspname = 'public'
   and c.relname in ('sessions', 'faiss_indexes');

-- Store a snapshot of the assembled DecisionResult for fast history rendering.
-- The structured tables (options, scores, …) remain for richer future use; for
-- MVP history we persist the rendered result as JSON on the decision row.

alter table public.decisions
  add column if not exists result_json jsonb;

-- Frequently we list a user's most recent decisions; index already exists on
-- (user_id, created_at). No extra index needed for the snapshot column.

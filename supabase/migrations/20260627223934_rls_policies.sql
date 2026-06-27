-- ─────────────────────────────────────────────────────────────────────────────
-- AI Decision OS — Row Level Security
--
-- Model: every row is owned (directly or via its parent decision) by a user.
-- Clients (authenticated role) get owner-scoped SELECT everywhere, plus full
-- CRUD on the tables users edit directly (decisions, preferences, outcomes,
-- shares). All AI-generated writes go through the service_role key, which
-- bypasses RLS — so child tables only need read policies for the client.
--
-- Patterns follow Supabase guidance: `TO authenticated`, ownership predicates
-- in USING, `(select auth.uid())` for performance, and both USING + WITH CHECK
-- on every UPDATE.
-- ─────────────────────────────────────────────────────────────────────────────

-- Enable RLS on every table --------------------------------------------------
alter table public.profiles              enable row level security;
alter table public.subscriptions         enable row level security;
alter table public.usage_counters        enable row level security;
alter table public.decisions             enable row level security;
alter table public.options               enable row level security;
alter table public.criteria              enable row level security;
alter table public.scores                enable row level security;
alter table public.pros_cons             enable row level security;
alter table public.risks                 enable row level security;
alter table public.evidence              enable row level security;
alter table public.agent_runs            enable row level security;
alter table public.simulations           enable row level security;
alter table public.preferences           enable row level security;
alter table public.preference_embeddings enable row level security;
alter table public.decision_outcomes     enable row level security;
alter table public.shares                enable row level security;

-- Profiles --------------------------------------------------------------------
create policy "profiles_select_own" on public.profiles
  for select to authenticated
  using ((select auth.uid()) = id);

create policy "profiles_update_own" on public.profiles
  for update to authenticated
  using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

-- Billing (read-only for clients; managed server-side via Stripe webhooks) ----
create policy "subscriptions_select_own" on public.subscriptions
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "usage_counters_select_own" on public.usage_counters
  for select to authenticated
  using ((select auth.uid()) = user_id);

-- Decisions (full CRUD for the owner) -----------------------------------------
create policy "decisions_select_own" on public.decisions
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "decisions_insert_own" on public.decisions
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "decisions_update_own" on public.decisions
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "decisions_delete_own" on public.decisions
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- Child tables owned via decision_id (client read-only) -----------------------
create policy "options_select_via_decision" on public.options
  for select to authenticated
  using (exists (
    select 1 from public.decisions d
    where d.id = options.decision_id and d.user_id = (select auth.uid())
  ));

create policy "criteria_select_via_decision" on public.criteria
  for select to authenticated
  using (exists (
    select 1 from public.decisions d
    where d.id = criteria.decision_id and d.user_id = (select auth.uid())
  ));

create policy "risks_select_via_decision" on public.risks
  for select to authenticated
  using (exists (
    select 1 from public.decisions d
    where d.id = risks.decision_id and d.user_id = (select auth.uid())
  ));

create policy "evidence_select_via_decision" on public.evidence
  for select to authenticated
  using (exists (
    select 1 from public.decisions d
    where d.id = evidence.decision_id and d.user_id = (select auth.uid())
  ));

create policy "agent_runs_select_via_decision" on public.agent_runs
  for select to authenticated
  using (exists (
    select 1 from public.decisions d
    where d.id = agent_runs.decision_id and d.user_id = (select auth.uid())
  ));

create policy "simulations_select_via_decision" on public.simulations
  for select to authenticated
  using (exists (
    select 1 from public.decisions d
    where d.id = simulations.decision_id and d.user_id = (select auth.uid())
  ));

-- Child tables owned via option_id → decision (two hops) ----------------------
create policy "scores_select_via_decision" on public.scores
  for select to authenticated
  using (exists (
    select 1 from public.options o
    join public.decisions d on d.id = o.decision_id
    where o.id = scores.option_id and d.user_id = (select auth.uid())
  ));

create policy "pros_cons_select_via_decision" on public.pros_cons
  for select to authenticated
  using (exists (
    select 1 from public.options o
    join public.decisions d on d.id = o.decision_id
    where o.id = pros_cons.option_id and d.user_id = (select auth.uid())
  ));

-- Preferences (user-managed, full CRUD) ---------------------------------------
create policy "preferences_select_own" on public.preferences
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "preferences_insert_own" on public.preferences
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "preferences_update_own" on public.preferences
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "preferences_delete_own" on public.preferences
  for delete to authenticated
  using ((select auth.uid()) = user_id);

create policy "preference_embeddings_select_own" on public.preference_embeddings
  for select to authenticated
  using ((select auth.uid()) = user_id);

-- Decision outcomes (user logs them) — owned via decision ----------------------
create policy "decision_outcomes_select_via_decision" on public.decision_outcomes
  for select to authenticated
  using (exists (
    select 1 from public.decisions d
    where d.id = decision_outcomes.decision_id and d.user_id = (select auth.uid())
  ));

create policy "decision_outcomes_insert_via_decision" on public.decision_outcomes
  for insert to authenticated
  with check (exists (
    select 1 from public.decisions d
    where d.id = decision_outcomes.decision_id and d.user_id = (select auth.uid())
  ));

create policy "decision_outcomes_update_via_decision" on public.decision_outcomes
  for update to authenticated
  using (exists (
    select 1 from public.decisions d
    where d.id = decision_outcomes.decision_id and d.user_id = (select auth.uid())
  ))
  with check (exists (
    select 1 from public.decisions d
    where d.id = decision_outcomes.decision_id and d.user_id = (select auth.uid())
  ));

-- Shares — owned via decision (public read is served server-side via BFF) ------
create policy "shares_select_via_decision" on public.shares
  for select to authenticated
  using (exists (
    select 1 from public.decisions d
    where d.id = shares.decision_id and d.user_id = (select auth.uid())
  ));

create policy "shares_insert_via_decision" on public.shares
  for insert to authenticated
  with check (exists (
    select 1 from public.decisions d
    where d.id = shares.decision_id and d.user_id = (select auth.uid())
  ));

create policy "shares_update_via_decision" on public.shares
  for update to authenticated
  using (exists (
    select 1 from public.decisions d
    where d.id = shares.decision_id and d.user_id = (select auth.uid())
  ))
  with check (exists (
    select 1 from public.decisions d
    where d.id = shares.decision_id and d.user_id = (select auth.uid())
  ));

create policy "shares_delete_via_decision" on public.shares
  for delete to authenticated
  using (exists (
    select 1 from public.decisions d
    where d.id = shares.decision_id and d.user_id = (select auth.uid())
  ));

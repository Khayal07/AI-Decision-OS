-- ─────────────────────────────────────────────────────────────────────────────
-- AI Decision OS — initial schema (plan §8)
-- Extensions, enums, helper functions, core tables, indexes, triggers.
-- RLS policies live in the companion migration.
-- ─────────────────────────────────────────────────────────────────────────────

-- Extensions ------------------------------------------------------------------
create extension if not exists "pgcrypto" with schema extensions; -- gen_random_uuid()
create extension if not exists "vector" with schema extensions;   -- Decision DNA embeddings

-- Enums -----------------------------------------------------------------------
create type public.plan_tier as enum ('free', 'pro', 'team');
create type public.decision_status as enum ('pending', 'running', 'done', 'failed');
create type public.criteria_direction as enum ('higher_better', 'lower_better');
create type public.proscons_kind as enum ('pro', 'con');
create type public.preference_source as enum ('explicit', 'learned');
create type public.agent_status as enum ('running', 'done', 'failed');

-- Helper: keep updated_at fresh -----------------------------------------------
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- Profiles (mirrors auth.users) -----------------------------------------------
create table public.profiles (
  id          uuid primary key references auth.users (id) on delete cascade,
  email       text,
  full_name   text,
  avatar_url  text,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create trigger profiles_set_updated_at
  before update on public.profiles
  for each row execute function public.set_updated_at();

-- Auto-provision a profile row on signup.
-- security definer is required to write to public.profiles from the auth trigger;
-- search_path is pinned and EXECUTE is revoked from callers (see below).
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.profiles (id, email, full_name, avatar_url)
  values (
    new.id,
    new.email,
    new.raw_user_meta_data ->> 'full_name',
    new.raw_user_meta_data ->> 'avatar_url'
  );
  return new;
end;
$$;

revoke execute on function public.handle_new_user() from public, anon, authenticated;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- Billing ---------------------------------------------------------------------
create table public.subscriptions (
  id                     uuid primary key default gen_random_uuid(),
  user_id                uuid not null references public.profiles (id) on delete cascade,
  plan                   public.plan_tier not null default 'free',
  status                 text not null default 'active',
  stripe_customer_id     text,
  stripe_subscription_id text,
  current_period_end     timestamptz,
  created_at             timestamptz not null default now(),
  updated_at             timestamptz not null default now(),
  unique (user_id)
);

create trigger subscriptions_set_updated_at
  before update on public.subscriptions
  for each row execute function public.set_updated_at();

create table public.usage_counters (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references public.profiles (id) on delete cascade,
  period_start   date not null default date_trunc('month', now())::date,
  decisions_used integer not null default 0,
  tokens_used    bigint not null default 0,
  unique (user_id, period_start)
);

-- Decisions -------------------------------------------------------------------
create table public.decisions (
  id               uuid primary key default gen_random_uuid(),
  user_id          uuid not null references public.profiles (id) on delete cascade,
  title            text,
  raw_input        text not null,
  decision_type    text,
  status           public.decision_status not null default 'pending',
  confidence       numeric(5, 2),
  winner_option_id uuid, -- FK added after options table exists
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);

create trigger decisions_set_updated_at
  before update on public.decisions
  for each row execute function public.set_updated_at();

create index decisions_user_created_idx on public.decisions (user_id, created_at desc);

create table public.options (
  id          uuid primary key default gen_random_uuid(),
  decision_id uuid not null references public.decisions (id) on delete cascade,
  name        text not null,
  score       numeric(6, 3),
  rank        integer,
  is_winner   boolean not null default false,
  summary     text,
  created_at  timestamptz not null default now()
);

create index options_decision_idx on public.options (decision_id);

alter table public.decisions
  add constraint decisions_winner_option_fk
  foreign key (winner_option_id) references public.options (id) on delete set null;

create table public.criteria (
  id          uuid primary key default gen_random_uuid(),
  decision_id uuid not null references public.decisions (id) on delete cascade,
  name        text not null,
  weight      numeric(5, 4) not null default 0,
  direction   public.criteria_direction not null default 'higher_better'
);

create index criteria_decision_idx on public.criteria (decision_id);

create table public.scores (
  id               uuid primary key default gen_random_uuid(),
  option_id        uuid not null references public.options (id) on delete cascade,
  criteria_id      uuid not null references public.criteria (id) on delete cascade,
  value            numeric(10, 4),
  normalized_value numeric(6, 4),
  rationale        text,
  unique (option_id, criteria_id)
);

create index scores_option_idx on public.scores (option_id);

create table public.pros_cons (
  id         uuid primary key default gen_random_uuid(),
  option_id  uuid not null references public.options (id) on delete cascade,
  kind       public.proscons_kind not null,
  text       text not null,
  weight     numeric(4, 3) not null default 0.5
);

create index pros_cons_option_idx on public.pros_cons (option_id);

create table public.risks (
  id          uuid primary key default gen_random_uuid(),
  decision_id uuid not null references public.decisions (id) on delete cascade,
  option_id   uuid references public.options (id) on delete cascade,
  description text not null,
  severity    integer check (severity between 1 and 5),
  likelihood  integer check (likelihood between 1 and 5),
  mitigation  text
);

create index risks_decision_idx on public.risks (decision_id);

create table public.evidence (
  id                 uuid primary key default gen_random_uuid(),
  decision_id        uuid not null references public.decisions (id) on delete cascade,
  claim              text not null,
  source_url         text,
  source_title       text,
  credibility_score  numeric(4, 3),
  supports_option_id uuid references public.options (id) on delete set null
);

create index evidence_decision_idx on public.evidence (decision_id);

create table public.agent_runs (
  id            uuid primary key default gen_random_uuid(),
  decision_id   uuid not null references public.decisions (id) on delete cascade,
  agent_name    text not null,
  model         text,
  input_tokens  integer,
  output_tokens integer,
  latency_ms    integer,
  status        public.agent_status not null default 'running',
  trace_id      text,
  created_at    timestamptz not null default now()
);

create index agent_runs_decision_idx on public.agent_runs (decision_id);

create table public.simulations (
  id          uuid primary key default gen_random_uuid(),
  decision_id uuid not null references public.decisions (id) on delete cascade,
  params      jsonb not null default '{}'::jsonb,
  result      jsonb not null default '{}'::jsonb,
  created_at  timestamptz not null default now()
);

create index simulations_decision_idx on public.simulations (decision_id);

-- Personalization (Decision DNA) ----------------------------------------------
create table public.preferences (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references public.profiles (id) on delete cascade,
  key        text not null,
  value      text,
  weight     numeric(5, 4) not null default 0,
  source     public.preference_source not null default 'explicit',
  updated_at timestamptz not null default now(),
  unique (user_id, key)
);

create trigger preferences_set_updated_at
  before update on public.preferences
  for each row execute function public.set_updated_at();

-- voyage-3 embeddings are 1024-dimensional
create table public.preference_embeddings (
  user_id    uuid primary key references public.profiles (id) on delete cascade,
  embedding  vector(1024),
  updated_at timestamptz not null default now()
);

create index preference_embeddings_vec_idx
  on public.preference_embeddings using hnsw (embedding vector_cosine_ops);

-- Outcomes & sharing ----------------------------------------------------------
create table public.decision_outcomes (
  id                     uuid primary key default gen_random_uuid(),
  decision_id            uuid not null references public.decisions (id) on delete cascade,
  chosen_option_id       uuid references public.options (id) on delete set null,
  user_confidence_rating integer check (user_confidence_rating between 1 and 5),
  outcome_note           text,
  logged_at              timestamptz not null default now(),
  unique (decision_id)
);

create table public.shares (
  id          uuid primary key default gen_random_uuid(),
  decision_id uuid not null references public.decisions (id) on delete cascade,
  public_slug text not null unique,
  is_active   boolean not null default true,
  created_at  timestamptz not null default now()
);

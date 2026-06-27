# Supabase

Database schema, migrations, and Row Level Security for AI Decision OS.

## Migrations

| File | Purpose |
| --- | --- |
| `migrations/20260627223933_init_schema.sql` | Extensions (pgvector), enums, core tables, indexes, `updated_at` + new-user triggers (plan §8) |
| `migrations/20260627223934_rls_policies.sql` | RLS enabled on every table + owner-scoped policies |

## Applying to your project

These files follow Supabase conventions but have **not** been applied to a live
database yet. To set up:

```bash
# one-time
supabase login
supabase link --project-ref <your-project-ref>

# apply migrations
supabase db push

# verify schema + security
supabase migration list
supabase db advisors            # check for RLS / security warnings, then fix
```

For local development with the full Supabase stack:

```bash
supabase start                  # requires Docker
supabase db reset               # applies all migrations to the local DB
```

## Security model

- Every table has RLS enabled.
- Clients (the `authenticated` role) get **owner-scoped SELECT** everywhere, plus
  full CRUD on tables users edit directly (`decisions`, `preferences`,
  `decision_outcomes`, `shares`).
- All AI-generated writes (options, scores, risks, evidence, agent_runs, …) go
  through the **service_role** key from the BFF / AI service, which bypasses RLS.
- The `service_role` key is server-only and must never reach the browser.

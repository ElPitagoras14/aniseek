# Upgrading

## Migration to dbmate (2.0.20 and later)

The database schema is managed by [dbmate](https://github.com/amacneil/dbmate) migrations under `dbmate/migrations/`, applied automatically by a one-shot `aniseek-migrate` service before the API and worker start. `postgres/init.sql` no longer exists.

The migrations ship inside the `ghcr.io/elpitagoras14/aniseek-migrate` image, published with the same version as the other services, so a deployment needs nothing on the host but `compose.yaml` and `.env`.

New deployments don't need anything else: the schema is built entirely from the migrations on first start.

### If your deployment mounted the migrations directory

If you mounted it (`./db:/db`, or an absolute path like `/dokploy-bk/aniseek/db:/db`), **remove that mount** when you move to the new image. Leaving it in place would shadow the packaged migrations with whatever is on the host — the migration step would still succeed, with the wrong files.

### If you are upgrading a deployment created before dbmate

dbmate needs to be told that the schema it already has matches the first migration, without re-running any SQL. Do this once, **before** pulling the new images:

1. Back up your database.
2. **Recommended**: verify your schema actually matches `dbmate/schema.sql` before assuming it does. Dump it with the same tool dbmate uses internally, so the comparison isn't skewed by a different `pg_dump` version:

   ```bash
   docker run --rm --entrypoint pg_dump ghcr.io/amacneil/dbmate:2.35.0 \
     --schema-only --no-owner --no-privileges "<your DB_URL>?sslmode=disable" \
     > real-schema.sql
   ```

   Diff it against `dbmate/schema.sql` — if you don't have the repository on the host, pull it out of the migrations image itself:

   ```bash
   docker run --rm --entrypoint cat ghcr.io/elpitagoras14/aniseek-migrate:latest \
     /db/schema.sql > expected-schema.sql
   ```

   (Ignore the `\restrict` line and the `schema_migrations` table/insert at the end — those are dbmate-only bookkeeping the real dump won't have.) Any other difference means your schema drifted from `init.sql` at some point and needs reconciling before continuing.
3. Connect to the database and register the first migration as already applied:

   ```sql
   CREATE TABLE IF NOT EXISTS public.schema_migrations (version varchar PRIMARY KEY);
   INSERT INTO public.schema_migrations (version) VALUES ('0001');
   ```

4. Pull and start the new version as usual (`docker compose up -d`). The `aniseek-migrate` service will find nothing pending and exit successfully; the API and worker start right after it.

Skipping step 3 makes `aniseek-migrate` fail with a "relation already exists" error on the first migration, which blocks the API and worker from starting — no data is affected, but the app stays down until the table above is created.

## `AUTH_ENABLED` default

If your deployment never set `AUTH_ENABLED`: an unset value now makes the frontend require login, matching what the backend has always enforced. Previously an unset value silently disabled the login screen while the API still rejected every request. If you rely on running without login, set `AUTH_ENABLED=false` explicitly before upgrading.

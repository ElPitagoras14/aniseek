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

## 3.1.0: API keys

Migration `0003` drops the `api_keys` and `api_scopes` tables from the initial schema and creates a new `api_keys` table (one key per user, stored as a hash). No code ever used the old tables, so nothing is lost unless you inserted rows into them by hand. Users generate their key from **Profile** (see [Deployment](deployment.md#api-keys)).

To roll back, run `dbmate down` for migration `0003` before starting the previous image; any keys generated in the meantime are lost.

## 3.0.0: users and access

3.0.0 introduces roles that the API actually enforces. Read this before upgrading; **registration changes behaviour**.

### What happens on first start

- **The admin becomes the owner.** The API promotes the oldest *active* user with role `admin` to **owner**, whatever their username is, keeping their password, saved list and history. A deactivated admin is skipped. You don't need `OWNER_USERNAME` / `OWNER_PASSWORD` in this case (they are ignored).
- **`guest` no longer exists.** Users with that role become `member`.
- **Registration is by invitation only.** Open sign-up used to work; now `POST /auth/register` answers 403 unless the person has an invitation. Owner and admins can create invitations or accounts from **User Management**, or reopen sign-up under User Management → Settings → Registration (set it to *Open*).
- **Some actions now need `admin`:** deleting downloaded files (Storage), creating franchises and listing users. Members lose them.
- **Sessions are stricter:** deactivated users are rejected immediately (not only at login), and changing a password closes the user's other sessions.
- **The `admin` / `admin123` seed is gone.** If you never changed that password, change it now from **Profile**.

### If the API doesn't start

If the instance has neither an owner nor an active admin (for example all admins were deactivated), the API needs `OWNER_USERNAME` and `OWNER_PASSWORD` to create one and will not start without them. See [Deployment](deployment.md#the-owner-account).

### Recovering the owner

There is no recovery command yet. If the owner loses their password and can't reach the UI, promote another user directly in the database (the unique index allows a single owner, so demote the current one first):

```sql
BEGIN;
UPDATE users SET role_id = (SELECT id FROM role_types WHERE name = 'admin')
  WHERE role_id = (SELECT id FROM role_types WHERE name = 'owner');
UPDATE users SET role_id = (SELECT id FROM role_types WHERE name = 'owner'),
                 is_active = TRUE
  WHERE username = '<the user who takes over>';
COMMIT;
```

The previous owner is now an `admin`, so the new owner can reset their password from **User Management**.

### Rolling back

1. Stop the API.
2. Run `dbmate down` for migration `0002` (the migrate image accepts `["--no-dump-schema", "down"]`).
3. Start the previous image.

The users stay, and the owner goes back to `admin`. Invitations, instance settings and the original `guest` role are not recovered (former guests stay `member`).

# Deployment

Ani Seek is designed for **local or self-hosted deployment** and does not include HTTPS natively.

For internet-facing deployments:

- Place the services behind a reverse proxy (Nginx, Traefik, Caddy) that handles TLS termination.
- Or use [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) for a zero-config HTTPS setup.
- Set `SECRET_KEY` to a long random value and choose a strong `OWNER_PASSWORD` (see below). There are no default credentials.
- Leave `API_URL` empty (the Docker default): the web container proxies `/api/` to the API through nginx, so the browser only talks to the web port.

## The owner account

On a **fresh install** the API creates the owner at startup from `OWNER_USERNAME` and `OWNER_PASSWORD` (set both in `.env`). They are only read while the instance has no owner; changing them afterwards does nothing, so change the password from the **Profile** page.

If you forget them, the symptom is easy to recognise:

- `aniseek-api` restarts in a loop (`restart: unless-stopped`, with a growing delay between attempts).
- `aniseek-web` never starts, because it waits for the API to be healthy, and `docker compose up -d` ends reporting that a dependency failed.
- The cause is in the logs: `docker compose logs aniseek-api` shows an error naming the missing or invalid variable (`OWNER_USERNAME` or `OWNER_PASSWORD`), or telling you the username is already taken by an existing user.

Add the variables to `.env` and run `docker compose up -d` again. No user is created while the error persists.

## API keys

Each user can generate one API key from **Profile → AI agents**, so AI agents can act as them over MCP with their current role. Only a hash is stored: the key is shown once, and regenerating it invalidates the previous one. The owner can see and revoke every user's key from **User Management**.

With `AUTH_ENABLED=false` (single-user mode) there is no login, so **anyone who can open the web UI can generate the owner's key**. Use that mode only on a trusted network.

The keys are used by the [MCP server](mcp.md), which the owner turns on from **Instance Settings**.

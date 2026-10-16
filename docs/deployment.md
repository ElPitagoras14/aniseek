# Deployment

Ani Seek is designed for **local or self-hosted deployment** and does not include HTTPS natively.

For internet-facing deployments:

- Place the services behind a reverse proxy (Nginx, Traefik, Caddy) that handles TLS termination.
- Or use [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) for a zero-config HTTPS setup.
- Set `SECRET_KEY` to a long random value and change the default admin credentials (`admin` / `admin123`).
- Leave `API_URL` empty (the Docker default): the web container proxies `/api/` to the API through nginx, so the browser only talks to the web port.

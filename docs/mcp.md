# MCP server

Ani Seek exposes a [Model Context Protocol](https://modelcontextprotocol.io) server so an AI agent can search, organize and download anime on behalf of a user. It is off by default and the owner turns it on for the whole instance.

## Enable it

1. As the owner, open **Instance Settings → MCP server** and turn on **Enable MCP server**.
2. Each user who wants to connect an agent opens **Profile → AI agents** and generates an API key. The key is shown once, together with the Claude Code command that already includes it; copy them then. The same section always shows the endpoint and the command with a placeholder for the key.

The endpoint is `https://<your-instance>/api/mcp` (Streamable HTTP, stateless). With the MCP turned off, the endpoint answers `404` as if it did not exist; existing API keys are kept and work again when it is turned back on.

An agent acts as the key's owner, with that user's **current** role: a role change or a deactivation takes effect on the next call. Revoking or regenerating the key cuts the agent off immediately.

## Connect a client

### Claude Code

```bash
claude mcp add --transport http aniseek https://<your-instance>/api/mcp \
  --header "Authorization: Bearer <your-api-key>"
```

### Claude Desktop

Claude Desktop launches local (stdio) servers from its config file, so it reaches Ani Seek through the [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) bridge (requires Node.js). In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aniseek": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://<your-instance>/api/mcp",
        "--header",
        "Authorization:${ANISEEK_AUTH}"
      ],
      "env": {
        "ANISEEK_AUTH": "Bearer <your-api-key>"
      }
    }
  }
}
```

The header value goes through `env` because some platforms split arguments that contain spaces.

Any other client that speaks Streamable HTTP works the same way: send the key as `Authorization: Bearer <key>`.

## Tools

| Tool | What it does | Minimum role |
|---|---|---|
| `search_anime` | Search the provider by title | member |
| `get_anime` | Details, related anime and every episode with its download status | member |
| `list_saved` | The user's saved anime | member |
| `list_airing` | Saved anime still airing, optionally for one weekday | member |
| `list_downloads` | The user's download history | member |
| `get_storage_usage` | Disk used per anime and in total | member |
| `get_stats` | Counts of saved anime, downloads and airing anime | member |
| `save_anime` / `unsave_anime` | Add to or remove from the saved list | member |
| `refresh_anime` | Sync an anime again (once every 5 minutes) | member |
| `download_episodes` | Request episode downloads, at most 25 new episodes per call | member |
| `get_download_status` | Status of episodes, including finished ones | member |
| `delete_anime_files` | Delete all downloaded files of an anime | admin |

An agent only sees the tools its user's role can use. `delete_anime_files` is marked as destructive, so clients ask for confirmation before running it.

`download_episodes` skips the episodes the user already requested (they do not count toward the 25) and reports each episode as `enqueued`, `already_downloaded`, `not_found` or `enqueue_failed`. A request with more than 25 new episodes is rejected whole; split it.

### Anime ids

Every anime id the MCP takes or returns has the form `<provider>:<slug>`, for example `animeav1:one-piece`. AnimeAV1 is the only provider today. The REST API keeps plain slugs.

## Single-user mode

With `AUTH_ENABLED=false` there is no login, so **anyone who can open the web UI can turn on the MCP and generate the owner's key**. The MCP still requires the key on every request. Use that mode only on a trusted network.

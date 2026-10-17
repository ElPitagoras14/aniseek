import { apiUrl } from "@/config";

// An empty API_URL means the API is served from this same origin.
export const MCP_ENDPOINT = `${apiUrl || window.location.origin}/api/mcp`;

export function claudeCodeCommand(apiKey = "<your-api-key>") {
	return `claude mcp add --transport http aniseek ${MCP_ENDPOINT} --header "Authorization: Bearer ${apiKey}"`;
}

export const MCP_DOCS_URL =
	"https://github.com/ElPitagoras14/aniseek/blob/main/docs/mcp.md";

import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { CircleAlert } from "lucide-react";
import { CopyButton } from "@/components/copy-button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { mcpStatusQueryOptions } from "@/features/access/api";
import { useHasRole } from "@/features/access/hooks/use-current-user";
import {
	claudeCodeCommand,
	MCP_DOCS_URL,
	MCP_ENDPOINT,
} from "@/features/access/lib/mcp";
import { cn } from "@/lib/utils";

const COMMAND = claudeCodeCommand();

// Endpoint and ready-to-copy client setup. Dimmed while the owner has the
// MCP server turned off, since nothing can connect then.
export function McpConnection() {
	const status = useQuery(mcpStatusQueryOptions);
	const isOwner = useHasRole("owner");

	if (status.isLoading) {
		return <Skeleton className="h-32 w-full" />;
	}
	const enabled = status.data?.enabled ?? false;

	return (
		<div className="flex flex-col gap-5">
			{!enabled && (
				<div className="flex items-start gap-2 rounded-lg border border-dashed p-3 text-sm text-muted-foreground">
					<CircleAlert className="mt-0.5 size-4 shrink-0" />
					<span>
						The MCP server is turned off for this instance, so agents cannot
						connect.{" "}
						{isOwner ? (
							<Link
								to="/instance-settings"
								hash="mcp"
								className="text-foreground underline underline-offset-2"
							>
								Turn it on in Instance Settings
							</Link>
						) : (
							"Ask the instance owner to turn it on."
						)}
					</span>
				</div>
			)}

			<div
				aria-disabled={!enabled}
				className={cn(
					"flex flex-col gap-5 transition-opacity",
					!enabled && "pointer-events-none opacity-50 select-none",
				)}
			>
				<div className="flex flex-col gap-2">
					<Label htmlFor="mcp-endpoint">MCP endpoint</Label>
					<div className="flex gap-2">
						<Input
							id="mcp-endpoint"
							readOnly
							disabled={!enabled}
							value={MCP_ENDPOINT}
							onFocus={(e) => e.target.select()}
							className="font-mono"
						/>
						<CopyButton
							text={MCP_ENDPOINT}
							label="Copy endpoint"
							disabled={!enabled}
						/>
					</div>
				</div>

				<div className="flex flex-col gap-2">
					<Label htmlFor="mcp-claude-code">Add to Claude Code</Label>
					<div className="flex items-start gap-2">
						<pre
							id="mcp-claude-code"
							className="min-w-0 flex-1 whitespace-pre-wrap break-all rounded-md border bg-muted/40 px-3 py-2 font-mono text-xs leading-relaxed"
						>
							<code>{COMMAND}</code>
						</pre>
						<CopyButton
							text={COMMAND}
							label="Copy Claude Code command"
							disabled={!enabled}
						/>
					</div>
					<p className="text-xs text-muted-foreground">
						Replace <code className="font-mono">&lt;your-api-key&gt;</code> with
						your key. Other clients, such as Claude Desktop:{" "}
						<a
							href={MCP_DOCS_URL}
							target="_blank"
							rel="noreferrer"
							className="underline underline-offset-2"
						>
							docs/mcp.md
						</a>
						.
					</p>
				</div>
			</div>
		</div>
	);
}

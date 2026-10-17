import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { Bot } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { settingsQueryOptions, updateMcpEnabled } from "@/features/access/api";
import { parseApiError } from "@/features/access/lib/parse-error";

export function McpSection() {
	const queryClient = useQueryClient();
	const settings = useQuery(settingsQueryOptions);

	const mutation = useMutation({
		mutationFn: updateMcpEnabled,
		onSuccess: (_, value) => {
			// Also refreshes the MCP status Profile reads (["settings", "mcp"]).
			queryClient.invalidateQueries({ queryKey: ["settings"] });
			toast.success(value ? "MCP server enabled" : "MCP server disabled");
		},
		onError: (error) => {
			toast.error(parseApiError(error, "Could not update the MCP server"));
		},
	});

	return (
		<div className="flex flex-col gap-4">
			<div className="flex items-center justify-between gap-4 rounded-lg border p-4">
				<div className="flex min-w-0 flex-col gap-1">
					<Label htmlFor="mcp-enabled" className="text-sm font-medium">
						Enable MCP server
					</Label>
					<span className="text-xs text-muted-foreground">
						When off, the endpoint answers as if it did not exist. API keys are
						kept.
					</span>
				</div>
				<Switch
					id="mcp-enabled"
					checked={settings.data?.mcpEnabled ?? false}
					disabled={!settings.data || mutation.isPending}
					onCheckedChange={(value) => mutation.mutate(value)}
				/>
			</div>
			<p className="text-xs text-muted-foreground">
				Each user connects their agents from their profile, with their own API
				key.
			</p>
			<div>
				<Button variant="outline" size="sm" asChild>
					<Link to="/profile" hash="ai-agents">
						<Bot />
						Connect your agents
					</Link>
				</Button>
			</div>
		</div>
	);
}

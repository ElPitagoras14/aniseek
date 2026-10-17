import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { KeyRound, Loader2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { CopyButton } from "@/components/copy-button";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
	generateApiKey,
	ownApiKeyQueryOptions,
	revokeOwnApiKey,
} from "@/features/access/api";
import { claudeCodeCommand } from "@/features/access/lib/mcp";
import { parseApiError } from "@/features/access/lib/parse-error";

function formatDateTime(iso: string | null) {
	if (!iso) return "Never";
	return new Date(iso).toLocaleString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
		hour: "numeric",
		minute: "2-digit",
	});
}

export function ApiKeySection() {
	const queryClient = useQueryClient();
	const apiKey = useQuery(ownApiKeyQueryOptions);
	// The full key is only ever returned by the generate call: keep it here,
	// show it once and drop it when the dialog closes.
	const [newKey, setNewKey] = useState<string | null>(null);

	const invalidate = () =>
		queryClient.invalidateQueries({ queryKey: ["api-keys"] });

	const generate = useMutation({
		mutationFn: generateApiKey,
		onSuccess: (created) => {
			invalidate();
			setNewKey(created.key);
		},
		onError: (error) => {
			toast.error(parseApiError(error, "Could not generate the API key"));
		},
	});

	const revoke = useMutation({
		mutationFn: revokeOwnApiKey,
		onSuccess: () => {
			invalidate();
			toast.success("API key revoked");
		},
		onError: (error) => {
			toast.error(parseApiError(error, "Could not revoke the API key"));
		},
	});

	const closeKeyDialog = () => setNewKey(null);

	return (
		<>
			{apiKey.isLoading ? (
				<Skeleton className="h-16 w-full" />
			) : apiKey.isError ? (
				<div className="text-sm">
					<span className="text-destructive">Failed to load the API key. </span>
					<Button
						variant="outline"
						size="sm"
						className="ml-2"
						onClick={() => apiKey.refetch()}
					>
						Retry
					</Button>
				</div>
			) : apiKey.data ? (
				<div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border p-3">
					<div className="flex min-w-0 flex-col gap-0.5">
						<code className="truncate text-sm font-medium">
							{apiKey.data.prefix}…
						</code>
						<span className="text-xs text-muted-foreground">
							Created {formatDateTime(apiKey.data.createdAt)} · Last used{" "}
							{formatDateTime(apiKey.data.lastUsedAt)}
						</span>
					</div>
					<div className="flex gap-2">
						<ConfirmDialog
							trigger={
								<Button variant="outline" size="sm">
									Regenerate
								</Button>
							}
							title="Regenerate API key?"
							description="The current key stops working right away. Agents using it must be updated with the new one."
							confirmLabel="Regenerate"
							onConfirm={() => generate.mutateAsync().catch(() => {})}
						/>
						<ConfirmDialog
							trigger={
								<Button variant="outline" size="sm">
									Revoke
								</Button>
							}
							title="Revoke API key?"
							description="The key stops working right away. You can generate a new one later."
							confirmLabel="Revoke"
							destructive
							onConfirm={() => revoke.mutateAsync().catch(() => {})}
						/>
					</div>
				</div>
			) : (
				<div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-dashed p-3">
					<span className="text-sm text-muted-foreground">
						You have no API key.
					</span>
					<Button
						size="sm"
						onClick={() => generate.mutate()}
						disabled={generate.isPending}
					>
						{generate.isPending ? (
							<Loader2 className="animate-spin" />
						) : (
							<KeyRound />
						)}
						Generate key
					</Button>
				</div>
			)}

			<Dialog
				open={newKey !== null}
				onOpenChange={(open) => !open && closeKeyDialog()}
			>
				<DialogContent className="sm:max-w-xl">
					<DialogHeader>
						<DialogTitle>API key ready</DialogTitle>
						<DialogDescription>
							Copy the key now: it will not be shown again.
						</DialogDescription>
					</DialogHeader>
					<div className="flex gap-2">
						<Input
							readOnly
							value={newKey ?? ""}
							onFocus={(e) => e.target.select()}
							className="font-mono"
						/>
						<CopyButton text={newKey ?? ""} label="Copy key" />
					</div>
					<div className="flex min-w-0 flex-col gap-2">
						<Label htmlFor="new-key-claude-code">
							Or add it to Claude Code
						</Label>
						<div className="flex items-start gap-2">
							<pre
								id="new-key-claude-code"
								className="min-w-0 flex-1 whitespace-pre-wrap break-all rounded-md border bg-muted/40 px-3 py-2 font-mono text-xs leading-relaxed"
							>
								<code>{claudeCodeCommand(newKey ?? "")}</code>
							</pre>
							<CopyButton
								text={claudeCodeCommand(newKey ?? "")}
								label="Copy Claude Code command"
							/>
						</div>
					</div>
					<DialogFooter>
						<Button onClick={closeKeyDialog}>Done</Button>
					</DialogFooter>
				</DialogContent>
			</Dialog>
		</>
	);
}

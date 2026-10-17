import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
	invitationsQueryOptions,
	revokeInvitation,
} from "@/features/access/api";
import { parseApiError } from "@/features/access/lib/parse-error";
import { ROLE_LABELS } from "@/features/access/lib/roles";
import type { AccessUser } from "@/features/access/types";
import { CreateInvitationDialog } from "./create-invitation-dialog";
import { GridMessage, GridRow, GridTable } from "./grid-table";

const COLS = "md:grid-cols-[150px_130px_1fr_120px_120px_100px]";

function formatDate(iso: string) {
	return new Date(iso).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	});
}

export function InvitationsTab({ me }: { me: AccessUser }) {
	const queryClient = useQueryClient();
	const invitations = useQuery(invitationsQueryOptions);

	const revoke = useMutation({
		mutationFn: revokeInvitation,
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: invitationsQueryOptions.queryKey,
			});
			toast.success("Invitation revoked");
		},
		onError: (error) => {
			toast.error(parseApiError(error, "Could not revoke the invitation"));
		},
	});

	const items = invitations.data?.items ?? [];

	return (
		<div className="flex flex-col gap-4">
			<div className="flex justify-end">
				<CreateInvitationDialog me={me} />
			</div>
			<GridTable
				cols={COLS}
				minWidth="md:min-w-[860px]"
				headers={[
					{ label: "Created by" },
					{ label: "Role" },
					{ label: "Used", center: true },
					{ label: "Created", center: true },
					{ label: "Expires", center: true },
					{ label: "Actions", center: true },
				]}
			>
				{invitations.isLoading ? (
					Array.from({ length: 3 }).map((_, i) => (
						// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton
						<GridRow key={i} cols={COLS}>
							<Skeleton className="h-4 w-24" />
							<Skeleton className="h-4 w-20" />
							<Skeleton className="h-4 w-28 md:mx-auto" />
							<Skeleton className="h-4 w-20 md:mx-auto" />
							<Skeleton className="h-4 w-20 md:mx-auto" />
							<Skeleton className="size-8 md:mx-auto" />
						</GridRow>
					))
				) : invitations.isError ? (
					<GridMessage>
						<span className="text-destructive">
							Failed to load invitations.{" "}
						</span>
						<Button
							variant="outline"
							size="sm"
							className="ml-2"
							onClick={() => invitations.refetch()}
						>
							Retry
						</Button>
					</GridMessage>
				) : items.length === 0 ? (
					<GridMessage>No invitations.</GridMessage>
				) : (
					items.map((invitation) => (
						<GridRow key={invitation.id} cols={COLS}>
							<span className="min-w-0 truncate text-sm font-medium">
								{invitation.createdBy ?? "—"}
							</span>
							<span className="text-sm font-medium">
								{ROLE_LABELS[invitation.role] ?? invitation.role}
							</span>
							{/* Only present once the invitation has been used. */}
							<span className="min-w-0 truncate text-sm md:text-center">
								{invitation.usedAt && (
									<>
										<span className="text-green-500">
											{formatDate(invitation.usedAt)}
										</span>
										{invitation.usedBy && (
											<span className="text-muted-foreground">
												{" "}
												· {invitation.usedBy}
											</span>
										)}
									</>
								)}
							</span>
							<span className="text-sm text-muted-foreground md:text-center">
								<span className="md:hidden">Created </span>
								{formatDate(invitation.createdAt)}
							</span>
							<span className="text-sm text-muted-foreground md:text-center">
								<span className="md:hidden">Expires </span>
								{formatDate(invitation.expiresAt)}
							</span>
							<div className="flex items-center max-md:ml-auto md:h-8 md:justify-center">
								{/* A used invitation can no longer be revoked. */}
								<Button
									variant="ghost"
									size="icon"
									className="text-muted-foreground hover:text-destructive"
									aria-label="Revoke invitation"
									disabled={!!invitation.usedAt || revoke.isPending}
									onClick={() => revoke.mutate(invitation.id)}
								>
									<Trash2 className="h-4 w-4" />
								</Button>
							</div>
						</GridRow>
					))
				)}
			</GridTable>
		</div>
	);
}

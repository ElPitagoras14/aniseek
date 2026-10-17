import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CircleCheck, CircleX, KeyRound, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
	apiKeysQueryOptions,
	revokeUserApiKey,
	updateManagedUser,
	usersQueryOptions,
} from "@/features/access/api";
import { parseApiError } from "@/features/access/lib/parse-error";
import { ROLE_LABELS } from "@/features/access/lib/roles";
import type { AccessUser, Role, UserApiKey } from "@/features/access/types";
import { CreateUserDialog } from "./create-user-dialog";
import { GridMessage, GridRow, GridTable } from "./grid-table";
import { ResetPasswordDialog } from "./reset-password-dialog";
import { RolePermissionsDialog } from "./role-permissions-dialog";

const COLS = "md:grid-cols-[1fr_180px_120px_130px_90px_120px]";
// The owner also sees each user's API key (api-keys, design D7).
const OWNER_COLS = "md:grid-cols-[1fr_180px_120px_130px_90px_120px_170px]";

// Mirror of the backend rule (assert_can_manage): the owner manages admins
// and members, an admin only members, nobody manages the owner or themself.
function canManage(me: AccessUser, target: AccessUser) {
	if (me.id === target.id || target.role === "owner") return false;
	return me.role === "owner" || target.role === "member";
}

function formatDate(iso: string | null) {
	if (!iso) return "";
	return new Date(iso).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	});
}

function ApiKeyCell({ apiKey }: { apiKey: UserApiKey | undefined }) {
	const queryClient = useQueryClient();

	if (!apiKey) {
		return <span className="text-sm text-muted-foreground">—</span>;
	}

	const revoke = () =>
		revokeUserApiKey(apiKey.userId)
			.then(() => {
				queryClient.invalidateQueries({ queryKey: ["api-keys"] });
				toast.success("API key revoked");
			})
			.catch((error) => {
				toast.error(parseApiError(error, "Could not revoke the API key"));
			});

	return (
		<div className="flex min-w-0 items-center gap-1">
			<div className="flex min-w-0 flex-col md:items-center">
				<code className="truncate text-xs font-medium">{apiKey.prefix}…</code>
				<span className="text-xs text-muted-foreground">
					{apiKey.lastUsedAt
						? `Used ${formatDate(apiKey.lastUsedAt)}`
						: "Never used"}
				</span>
			</div>
			<ConfirmDialog
				trigger={
					<Button
						variant="ghost"
						size="icon-sm"
						aria-label={`Revoke API key of ${apiKey.username}`}
					>
						<KeyRound className="text-destructive" />
					</Button>
				}
				title="Revoke API key?"
				description={`${apiKey.username}'s key stops working right away. They can generate a new one from their profile.`}
				confirmLabel="Revoke"
				destructive
				onConfirm={revoke}
			/>
		</div>
	);
}

export function UsersTab({ me }: { me: AccessUser }) {
	const queryClient = useQueryClient();
	const users = useQuery(usersQueryOptions);
	const isOwner = me.role === "owner";
	const cols = isOwner ? OWNER_COLS : COLS;
	const apiKeys = useQuery({ ...apiKeysQueryOptions, enabled: isOwner });
	const apiKeyByUser = useMemo(
		() => new Map((apiKeys.data?.items ?? []).map((k) => [k.userId, k])),
		[apiKeys.data],
	);
	const [search, setSearch] = useState("");
	const [direction, setDirection] = useState<"asc" | "desc">("asc");

	// Local only (no fetch): filter by username, sort alphabetically, and keep
	// the current user on top whatever the direction is.
	const rows = useMemo(() => {
		const term = search.trim().toLowerCase();
		const matching = (users.data?.items ?? []).filter((u) =>
			u.username.toLowerCase().includes(term),
		);
		const sign = direction === "asc" ? 1 : -1;
		const others = matching
			.filter((u) => u.id !== me.id)
			.sort(
				(a, b) =>
					sign *
					a.username.localeCompare(b.username, undefined, {
						sensitivity: "base",
					}),
			);
		return [...matching.filter((u) => u.id === me.id), ...others];
	}, [users.data, search, direction, me.id]);

	const mutation = useMutation({
		mutationFn: ({
			id,
			...payload
		}: {
			id: string;
			isActive?: boolean;
			role?: Role;
		}) => updateManagedUser(id, payload),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: usersQueryOptions.queryKey });
			toast.success("User updated");
		},
		onError: (error) => {
			toast.error(parseApiError(error, "Could not update the user"));
		},
	});

	return (
		<div className="flex flex-col gap-4">
			<div className="flex items-center justify-between gap-3">
				<div className="relative w-full max-w-xl">
					<Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
					<Input
						value={search}
						onChange={(e) => setSearch(e.target.value)}
						placeholder="Search by username…"
						aria-label="Search users"
						className="pl-9"
					/>
				</div>
				<div className="flex shrink-0 items-center gap-3">
					<RolePermissionsDialog />
					<CreateUserDialog me={me} />
				</div>
			</div>

			<GridTable
				cols={cols}
				minWidth={isOwner ? "md:min-w-[1050px]" : undefined}
				headers={[
					{
						label: "User",
						sort: {
							direction,
							onToggle: () =>
								setDirection((d) => (d === "asc" ? "desc" : "asc")),
						},
					},
					{ label: "Role", center: true },
					{ label: "Status", center: true },
					{ label: "Created", center: true },
					{ label: "Password", center: true },
					{ label: "Access", center: true },
					...(isOwner ? [{ label: "API key", center: true }] : []),
				]}
			>
				{users.isLoading ? (
					Array.from({ length: 4 }).map((_, i) => (
						// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton
						<GridRow key={i} cols={cols}>
							<Skeleton className="h-4 w-40" />
							<Skeleton className="h-7 w-28 md:mx-auto" />
							<Skeleton className="h-7 w-20 md:mx-auto" />
							<Skeleton className="hidden h-4 w-20 md:mx-auto md:block" />
							<Skeleton className="size-8 md:mx-auto" />
							<Skeleton className="h-7 w-20 md:mx-auto" />
							{isOwner && <Skeleton className="h-7 w-24 md:mx-auto" />}
						</GridRow>
					))
				) : users.isError ? (
					<GridMessage>
						<span className="text-destructive">Failed to load users. </span>
						<Button
							variant="outline"
							size="sm"
							className="ml-2"
							onClick={() => users.refetch()}
						>
							Retry
						</Button>
					</GridMessage>
				) : rows.length === 0 ? (
					<GridMessage>No users match your search.</GridMessage>
				) : (
					rows.map((user) => {
						const manageable = canManage(me, user);
						return (
							<GridRow key={user.id} cols={cols}>
								<div className="min-w-0 flex-1 truncate font-medium md:flex-none">
									{user.username}
									{user.id === me.id && (
										<span className="ml-1.5 text-xs font-normal text-muted-foreground">
											(you)
										</span>
									)}
								</div>
								<div className="md:flex md:justify-center">
									{manageable && me.role === "owner" ? (
										<Select
											value={user.role}
											onValueChange={(role) =>
												mutation.mutate({ id: user.id, role: role as Role })
											}
											disabled={mutation.isPending}
										>
											<SelectTrigger size="sm" className="w-36">
												<SelectValue />
											</SelectTrigger>
											<SelectContent>
												<SelectItem value="member">Member</SelectItem>
												<SelectItem value="admin">Administrator</SelectItem>
											</SelectContent>
										</Select>
									) : (
										<span className="text-sm font-medium">
											{ROLE_LABELS[user.role] ?? user.role}
										</span>
									)}
								</div>
								<div className="md:flex md:justify-center">
									{user.isActive ? (
										<CircleCheck
											className="size-5 text-green-500"
											aria-label="Active"
										/>
									) : (
										<CircleX
											className="size-5 text-red-500"
											aria-label="Disabled"
										/>
									)}
								</div>
								<span className="hidden text-center text-sm text-muted-foreground md:block">
									{formatDate(user.createdAt)}
								</span>
								<div className="flex items-center max-md:ml-auto md:justify-center">
									{manageable && <ResetPasswordDialog user={user} />}
								</div>
								<div className="flex items-center md:justify-center">
									{manageable && (
										<Button
											variant="outline"
											size="sm"
											className="w-20"
											disabled={mutation.isPending}
											onClick={() =>
												mutation.mutate({
													id: user.id,
													isActive: !user.isActive,
												})
											}
										>
											{user.isActive ? "Disable" : "Enable"}
										</Button>
									)}
								</div>
								{isOwner && (
									<div className="flex items-center max-md:basis-full md:justify-center">
										<ApiKeyCell apiKey={apiKeyByUser.get(user.id)} />
									</div>
								)}
							</GridRow>
						);
					})
				)}
			</GridTable>
		</div>
	);
}

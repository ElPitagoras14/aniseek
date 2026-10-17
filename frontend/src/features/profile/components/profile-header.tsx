import { UserRound } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ROLE_LABELS } from "@/features/access/lib/roles";
import { useProfile } from "../hooks/use-profile";

function formatDate(iso: string): string {
	return new Date(iso).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	});
}

// Identity and role come from /users/me (the token role can be stale).
export function ProfileHeader() {
	const { data: profile } = useProfile();

	return (
		<div className="flex items-center gap-3">
			<div className="flex size-11 shrink-0 items-center justify-center rounded-full bg-primary/15">
				{profile?.avatarUrl ? (
					<img
						src={profile.avatarUrl}
						alt={profile.username}
						className="size-full rounded-full object-cover"
					/>
				) : (
					<UserRound className="size-5 text-primary" />
				)}
			</div>
			{profile ? (
				<div className="flex min-w-0 flex-col gap-0.5">
					<div className="flex min-w-0 items-center gap-2">
						<p className="truncate font-semibold">{profile.username}</p>
						<Badge variant="secondary">
							{ROLE_LABELS[profile.role] ?? profile.role}
						</Badge>
					</div>
					{profile.createdAt && (
						<p className="text-xs text-muted-foreground">
							Member since {formatDate(profile.createdAt)}
						</p>
					)}
				</div>
			) : (
				<div className="flex flex-col gap-2">
					<Skeleton className="h-5 w-40" />
					<Skeleton className="h-4 w-32" />
				</div>
			)}
		</div>
	);
}

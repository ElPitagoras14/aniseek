import { Calendar, Clock, ShieldCheck, UserRound } from "lucide-react";
import { useAuth } from "@/auth";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useProfile } from "../hooks/use-profile";

const ROLE_LABELS: Record<string, string> = {
	admin: "Administrator",
	member: "Member",
	guest: "Guest",
};

function formatDate(iso: string): string {
	return new Date(iso).toLocaleDateString("en-US", {
		month: "long",
		day: "numeric",
		year: "numeric",
	});
}

function relativeTime(unixSec: number): string {
	const diff = Math.floor(Date.now() / 1000 - unixSec);
	if (diff < 60) return "Just now";
	if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
	if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
	return new Date(unixSec * 1000).toLocaleDateString("en-US", {
		month: "long",
		day: "numeric",
		year: "numeric",
	});
}

export function ProfileInfoCard() {
	const { user } = useAuth();
	const { data: profile } = useProfile();

	const roleLabel = ROLE_LABELS[user?.role ?? ""] ?? user?.role ?? "";

	return (
		<Card>
			<CardContent className="flex flex-col gap-5 p-6">
				<div className="flex flex-col items-center gap-3 py-2">
					<div className="flex size-20 items-center justify-center rounded-full bg-primary/15">
						{user?.avatarUrl ? (
							<img
								src={user.avatarUrl}
								alt={user.username}
								className="size-full rounded-full object-cover"
							/>
						) : (
							<UserRound className="size-9 text-primary" />
						)}
					</div>
					<div className="text-center">
						<p className="text-lg font-bold">{user?.username}</p>
						<p className="text-sm text-muted-foreground">{roleLabel}</p>
					</div>
				</div>

				<Separator />

				<div className="flex flex-col gap-4">
					<div className="flex items-center gap-3">
						<ShieldCheck className="size-4 shrink-0 text-muted-foreground" />
						<div>
							<p className="text-xs text-muted-foreground">Role</p>
							<p className="text-sm font-medium">{user?.role}</p>
						</div>
					</div>

					{profile?.createdAt && (
						<div className="flex items-center gap-3">
							<Calendar className="size-4 shrink-0 text-muted-foreground" />
							<div>
								<p className="text-xs text-muted-foreground">Member since</p>
								<p className="text-sm font-medium">
									{formatDate(profile.createdAt)}
								</p>
							</div>
						</div>
					)}

					{user?.loginAt && (
						<div className="flex items-center gap-3">
							<Clock className="size-4 shrink-0 text-muted-foreground" />
							<div>
								<p className="text-xs text-muted-foreground">Last login</p>
								<p className="text-sm font-medium">
									{relativeTime(user.loginAt)}
								</p>
							</div>
						</div>
					)}
				</div>
			</CardContent>
		</Card>
	);
}

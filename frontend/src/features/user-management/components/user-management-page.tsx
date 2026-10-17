import { Navigate } from "@tanstack/react-router";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCurrentUser } from "@/features/access/hooks/use-current-user";
import { hasRole } from "@/features/access/lib/roles";
import { InvitationsTab } from "./invitations-tab";
import { UsersTab } from "./users-tab";

export function UserManagementPage() {
	const { data: me, isLoading } = useCurrentUser();

	if (isLoading) {
		return (
			<div className="p-4 md:p-6">
				<Skeleton className="h-8 w-48" />
			</div>
		);
	}
	// The backend rejects these calls anyway; this just keeps members out of
	// a page that cannot work for them.
	if (!me || !hasRole(me.role, "admin")) {
		return <Navigate to="/home" replace />;
	}

	return (
		<div className="flex flex-col gap-6 p-4 md:p-6">
			<div>
				<h1 className="text-2xl font-semibold">User Management</h1>
				<p className="text-sm text-muted-foreground">
					Manage accounts and invitations
				</p>
			</div>

			<Tabs defaultValue="users" className="gap-5">
				<TabsList className="h-auto w-full max-w-xs">
					<TabsTrigger value="users" className="w-full">
						Users
					</TabsTrigger>
					<TabsTrigger value="invitations" className="w-full">
						Invitations
					</TabsTrigger>
				</TabsList>
				<TabsContent value="users" className="pt-1">
					<UsersTab me={me} />
				</TabsContent>
				<TabsContent value="invitations" className="pt-1">
					<InvitationsTab me={me} />
				</TabsContent>
			</Tabs>
		</div>
	);
}

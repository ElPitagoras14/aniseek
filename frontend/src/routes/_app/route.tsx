import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { NotFoundContent } from "@/components/not-found";
import { isAuthEnabled } from "@/config";
import { AppShell } from "@/features/root/components/app-shell";

export const Route = createFileRoute("/_app")({
	beforeLoad: async ({ context, location }) => {
		// Single-user mode: the backend resolves every request as the owner, so
		// there is nothing to log in to.
		if (!isAuthEnabled) {
			return;
		}
		if (!context.auth.isAuthenticated) {
			throw redirect({
				to: "/login",
				search: { redirect: location.href },
			});
		}
	},
	component: RouteComponent,
	notFoundComponent: NotFoundContent,
});

function RouteComponent() {
	return (
		<AppShell>
			<Outlet />
		</AppShell>
	);
}

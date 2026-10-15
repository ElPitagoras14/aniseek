import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { api } from "@/api";
import { NotFoundContent } from "@/components/not-found";
import { isAuthEnabled } from "@/config";
import { AppShell } from "@/features/root/components/app-shell";

interface LoginResponse {
	payload: { access: string; refresh: string };
}

export const Route = createFileRoute("/_app")({
	beforeLoad: async ({ context, location }) => {
		if (!isAuthEnabled) {
			if (!context.auth.isAuthenticated) {
				try {
					const { data } = await api.post<LoginResponse>("/auth/login", {
						username: "admin",
						password: "admin123",
					});
					context.auth.login(data.payload.access);
				} catch {}
			}
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

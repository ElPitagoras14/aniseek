import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { api } from "@/api";
import { NotFoundContent } from "@/components/not-found";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";
import { isAuthEnabled } from "@/config";
import { AppSidebar } from "@/features/root/components/app-sidebar";
import { MobileHeader } from "@/features/root/components/mobile-header";

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
		<div>
			<SidebarProvider>
				<TooltipProvider>
					<AppSidebar variant="sidebar" />
					<SidebarInset>
						<MobileHeader />
						<Outlet />
					</SidebarInset>
				</TooltipProvider>
			</SidebarProvider>
		</div>
	);
}

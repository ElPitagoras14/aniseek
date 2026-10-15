import { TanStackDevtools } from "@tanstack/react-devtools";
import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtoolsPanel } from "@tanstack/react-router-devtools";

import "../styles.css";
import type { AuthContext } from "@/auth";
import { NotFound } from "@/components/not-found";
import { Toaster } from "@/components/ui/sonner";
import { useIsMobile } from "@/hooks/use-mobile";

interface MyRouterContext {
	auth: AuthContext;
}

// Lift toasts above the mobile bottom nav (h-16 + safe area)
const MOBILE_TOAST_OFFSET = {
	bottom: "calc(4rem + env(safe-area-inset-bottom) + 16px)",
};

export const Route = createRootRouteWithContext<MyRouterContext>()({
	component: RootComponent,
	notFoundComponent: NotFound,
});

function RootComponent() {
	const isMobile = useIsMobile();

	return (
		<>
			<Outlet />
			<Toaster
				position="bottom-right"
				offset={isMobile ? MOBILE_TOAST_OFFSET : undefined}
				mobileOffset={isMobile ? MOBILE_TOAST_OFFSET : undefined}
			/>
			<TanStackDevtools
				config={{
					position: "bottom-right",
				}}
				plugins={[
					{
						name: "TanStack Router",
						render: <TanStackRouterDevtoolsPanel />,
					},
				]}
			/>
		</>
	);
}

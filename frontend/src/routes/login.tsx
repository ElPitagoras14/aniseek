import { createFileRoute, redirect } from "@tanstack/react-router";
import { z } from "zod";
import { isAuthEnabled } from "@/config";
import { LoginCard } from "@/features/auth/components/login-card";

const loginSearchSchema = z.object({
	redirect: z.string().optional(),
});

export const Route = createFileRoute("/login")({
	validateSearch: loginSearchSchema,
	beforeLoad: async ({ context, search }) => {
		if (!isAuthEnabled) {
			throw redirect({ to: "/home" });
		}
		if (context.auth.isAuthenticated) {
			throw redirect({ to: search.redirect ?? "/home" });
		}
	},
	component: RouteComponent,
});

function RouteComponent() {
	return <LoginCard />;
}

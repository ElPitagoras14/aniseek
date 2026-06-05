import { createFileRoute, redirect } from "@tanstack/react-router";
import { z } from "zod";
import { api } from "@/api";
import { isAuthEnabled } from "@/config";
import { LoginCard } from "@/features/auth/components/login-card";

const loginSearchSchema = z.object({
	redirect: z.string().optional(),
});

export const Route = createFileRoute("/login")({
	validateSearch: loginSearchSchema,
	beforeLoad: async ({ context, search }) => {
		if (!isAuthEnabled) {
			try {
				const { data } = await api.post<{ payload: { access: string } }>(
					"/auth/login",
					{ username: "admin", password: "admin123" },
				);
				context.auth.login(data.payload.access);
			} catch {}
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

import { createFileRoute, redirect } from "@tanstack/react-router";
import { z } from "zod";
import { isAuthEnabled } from "@/config";
import { RegisterCard } from "@/features/auth/components/register-card";

const registerSearchSchema = z.object({
	invite: z.string().optional(),
});

export const Route = createFileRoute("/register")({
	validateSearch: registerSearchSchema,
	beforeLoad: async ({ context }) => {
		// Single-user mode has no accounts to create.
		if (!isAuthEnabled || context.auth.isAuthenticated) {
			throw redirect({ to: "/home" });
		}
	},
	component: RouteComponent,
});

function RouteComponent() {
	const { invite } = Route.useSearch();
	return <RegisterCard invitationToken={invite} />;
}

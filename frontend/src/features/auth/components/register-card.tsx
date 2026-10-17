import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { ArrowLeft, Clapperboard, Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { registrationPolicyQueryOptions } from "@/features/access/api";
import { LoginFooter } from "./login-footer";
import { RegisterForm } from "./register-form";

export function RegisterCard({
	invitationToken,
}: {
	invitationToken: string | undefined;
}) {
	const policy = useQuery(registrationPolicyQueryOptions);

	// With an invitation the form always works (any policy); without one it
	// only works when the instance allows open registration.
	const canRegister = !!invitationToken || policy.data === "open";

	return (
		<div className="min-h-svh flex items-center justify-center p-4 bg-background">
			<div className="w-full max-w-sm sm:max-w-md mx-auto flex flex-col gap-3">
				<Link
					to="/login"
					className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors w-fit"
				>
					<ArrowLeft className="size-3.5" />
					Back to login
				</Link>
				<Card>
					<CardContent className="p-4 sm:p-6 flex flex-col gap-8">
						<div className="flex flex-col items-center gap-2 text-center">
							<Clapperboard className="size-10 text-muted-foreground" />
							<h1 className="text-2xl font-bold tracking-tight">
								Create your account
							</h1>
							{invitationToken && (
								<p className="text-sm text-muted-foreground">
									You were invited to join this instance.
								</p>
							)}
						</div>
						{!invitationToken && policy.isLoading ? (
							<Loader2 className="mx-auto size-5 animate-spin text-muted-foreground" />
						) : canRegister ? (
							<RegisterForm invitationToken={invitationToken} />
						) : (
							<p className="text-center text-sm text-muted-foreground">
								Registration on this instance is by invitation only. Ask an
								administrator for an invitation link.
							</p>
						)}
						<LoginFooter />
					</CardContent>
				</Card>
			</div>
		</div>
	);
}

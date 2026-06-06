import { Link } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { LoginFooter } from "./login-footer";
import { LoginForm } from "./login-form";
import { LoginHeader } from "./login-header";

export function LoginCard() {
	return (
		<div className="min-h-svh flex items-center justify-center p-4 bg-background">
			<div className="w-full max-w-sm sm:max-w-md mx-auto flex flex-col gap-3">
				<Link
					to="/"
					className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors w-fit"
				>
					<ArrowLeft className="size-3.5" />
					Back to home
				</Link>
				<Card>
					<CardContent className="p-4 sm:p-6 flex flex-col gap-8">
						<LoginHeader />
						<LoginForm />
						<LoginFooter />
					</CardContent>
				</Card>
			</div>
		</div>
	);
}

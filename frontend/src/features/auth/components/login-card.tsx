import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { LoginFooter } from "./login-footer";
import { LoginForm } from "./login-form";
import { LoginHeader } from "./login-header";

export function LoginCard() {
	return (
		<div className="min-h-svh flex items-center justify-center p-4 bg-background">
			<Card className="w-full max-w-sm sm:max-w-md mx-auto">
				<CardContent className="p-4 sm:p-6 flex flex-col gap-4">
					<LoginHeader />
					<Separator />
					<LoginForm />
					<Separator />
					<LoginFooter />
				</CardContent>
			</Card>
		</div>
	);
}

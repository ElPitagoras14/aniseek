import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { LandingLogo } from "./landing-logo";

export function LandingNavbar() {
	return (
		<header className="sticky top-0 z-20 border-b bg-background/80 backdrop-blur-sm">
			<div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 md:px-6 lg:px-8">
				<LandingLogo showBadge />
				<Button asChild variant="ghost" size="lg">
					<Link to="/login">Sign in</Link>
				</Button>
			</div>
		</header>
	);
}

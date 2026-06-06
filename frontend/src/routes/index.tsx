import { createFileRoute } from "@tanstack/react-router";
import { LandingCta } from "@/features/landing/components/landing-cta";
import { LandingFeatures } from "@/features/landing/components/landing-features";
import { LandingFooter } from "@/features/landing/components/landing-footer";
import { LandingHero } from "@/features/landing/components/landing-hero";
import { LandingHowItWorks } from "@/features/landing/components/landing-how-it-works";
import { LandingNavbar } from "@/features/landing/components/landing-navbar";

export const Route = createFileRoute("/")({ component: LandingPage });

function LandingPage() {
	return (
		<div className="min-h-screen bg-background text-foreground flex flex-col">
			<LandingNavbar />
			<main className="flex-1">
				<LandingHero />
				<LandingFeatures />
				<LandingHowItWorks />
				<LandingCta />
			</main>
			<LandingFooter />
		</div>
	);
}

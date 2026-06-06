import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";

export function LandingCta() {
	return (
		<section className="py-16">
			<div className="mx-auto w-full max-w-6xl px-4 md:px-6 lg:px-8">
				<div className="rounded-xl border bg-card px-8 py-14 text-center">
					<h2 className="text-3xl font-bold tracking-tight">
						Start exploring anime today
					</h2>
					<p className="mx-auto mt-3 max-w-xl text-muted-foreground">
						Join AniSeek and take control of your anime library. Search across
						sources, download episodes, and never lose track of what you&apos;re
						watching.
					</p>
					<div className="mt-8">
						<Button asChild size="lg">
							<Link to="/login">Get started, it&apos;s free</Link>
						</Button>
					</div>
				</div>
			</div>
		</section>
	);
}

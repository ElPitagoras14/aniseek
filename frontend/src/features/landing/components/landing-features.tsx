import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { LANDING_FEATURES } from "../data";

export function LandingFeatures() {
	return (
		<section id="features" className="py-16 md:py-24">
			<div className="mx-auto w-full max-w-6xl px-4 md:px-6 lg:px-8">
				<h2 className="mb-10 text-center text-3xl font-bold tracking-tight">
					Everything you need to manage your anime
				</h2>
				<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
					{LANDING_FEATURES.map((feature) => (
						<Card
							key={feature.title}
							className="transition-colors hover:bg-muted/50"
						>
							<CardHeader className="flex flex-row items-center gap-3 pb-2">
								<feature.icon
									className={cn("size-5 shrink-0", feature.iconClassName)}
								/>
								<CardTitle className="text-base">{feature.title}</CardTitle>
							</CardHeader>
							<CardContent>
								<p className="text-sm text-muted-foreground">
									{feature.description}
								</p>
							</CardContent>
						</Card>
					))}
				</div>
			</div>
		</section>
	);
}

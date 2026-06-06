import { Card, CardContent } from "@/components/ui/card";
import { LANDING_STEPS } from "../data";

export function LandingHowItWorks() {
	return (
		<section id="how-it-works" className="py-16 md:py-24">
			<div className="mx-auto w-full max-w-6xl px-4 md:px-6 lg:px-8">
				<h2 className="mb-10 text-center text-3xl font-bold tracking-tight">
					How it works
				</h2>
				<div className="grid gap-6 md:grid-cols-3">
					{LANDING_STEPS.map((step) => (
						<Card
							key={step.number}
							className="flex flex-col items-center text-center transition-colors hover:bg-muted/50"
						>
							<CardContent className="flex flex-col items-center">
								<step.icon className={`mb-3 size-8 ${step.iconClassName}`} />
								<h3 className="mb-2 text-lg font-semibold">{step.title}</h3>
								<p className="text-sm text-muted-foreground">
									{step.description}
								</p>
							</CardContent>
						</Card>
					))}
				</div>
			</div>
		</section>
	);
}

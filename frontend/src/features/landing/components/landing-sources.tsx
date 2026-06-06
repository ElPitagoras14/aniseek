import { Badge } from "@/components/ui/badge";
import { LANDING_SOURCES } from "../data";

export function LandingSources() {
	return (
		<section className="py-12">
			<div className="mx-auto w-full max-w-6xl px-4 md:px-6 lg:px-8">
				<div className="flex flex-col items-center gap-4">
					<div className="flex flex-wrap items-center justify-center gap-3">
						{LANDING_SOURCES.map((src) => (
							<Badge
								key={src}
								variant="secondary"
								className="px-4 py-1.5 text-sm"
							>
								{src}
							</Badge>
						))}
					</div>
				</div>
			</div>
		</section>
	);
}

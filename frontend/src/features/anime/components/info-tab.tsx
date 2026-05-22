import { Link } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";
import type { AnimeDetail } from "@/features/anime/types";

function translateRelatedType(type: string): string {
	switch (type) {
		case "sequel":
			return "Sequel";
		case "prequel":
			return "Prequel";
		case "spin_off":
			return "Spin-off";
		case "side_story":
			return "Side Story";
		default:
			return type.charAt(0).toUpperCase() + type.slice(1);
	}
}

interface InfoTabProps {
	anime: AnimeDetail;
}

export function InfoTab({ anime }: InfoTabProps) {
	return (
		<div className="flex flex-col gap-4">
			<div className="flex flex-col gap-2">
				<h3 className="text-base font-semibold">Synopsis</h3>
				<p className="text-sm text-muted-foreground whitespace-pre-line">
					{anime.description.replace(/\\n/g, "\n")}
				</p>
			</div>

			{anime.genres.length > 0 && (
				<div className="flex flex-col gap-2">
					<h3 className="text-base font-semibold">Genres</h3>
					<div className="flex flex-wrap gap-2">
						{anime.genres.map((genre) => (
							<Badge key={genre} variant="secondary" className="text-sm px-4 py-3">
								{genre}
							</Badge>
						))}
					</div>
				</div>
			)}

			{anime.relatedInfo.length > 0 && (
				<div className="flex flex-col gap-3">
					<h3 className="text-base font-semibold">Related Anime</h3>
					<div className="flex flex-wrap gap-3">
						{anime.relatedInfo.map((related) => (
							<Link
								key={related.id}
								to="/anime/$slug"
								params={{ slug: related.id }}
								className="rounded-md border bg-card p-3 flex flex-col gap-1 text-sm hover:bg-accent transition-colors"
							>
								<span>{related.title}</span>
								<Badge variant="secondary">
									{translateRelatedType(related.type)}
								</Badge>
							</Link>
						))}
					</div>
				</div>
			)}
		</div>
	);
}

import { Link } from "@tanstack/react-router";
import type { InEmissionAnime } from "../types";

interface CalendarAnimeCardProps {
	anime: InEmissionAnime;
}

export function CalendarAnimeCard({ anime }: CalendarAnimeCardProps) {
	return (
		<Link
			to="/anime/$slug"
			params={{ slug: anime.id }}
			className="flex flex-col gap-1.5 group"
		>
			<div className="relative aspect-[2/3] w-full overflow-hidden rounded-md">
				<img
					src={anime.poster}
					alt={anime.title}
					loading="lazy"
					className="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"
				/>
			</div>
			<span className="text-xs font-medium leading-tight line-clamp-2 px-0.5">
				{anime.title}
			</span>
		</Link>
	);
}

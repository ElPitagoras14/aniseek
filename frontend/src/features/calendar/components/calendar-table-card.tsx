import { Link } from "@tanstack/react-router";
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger,
} from "@/components/ui/tooltip";
import type { InEmissionAnime } from "../types";

interface CalendarTableCardProps {
	anime: InEmissionAnime;
}

export function CalendarTableCard({ anime }: CalendarTableCardProps) {
	return (
		<Tooltip>
			<TooltipTrigger asChild>
				<Link
					to="/anime/$slug"
					params={{ slug: anime.id }}
					className="block rounded-md border bg-card px-2 py-2 text-center text-xs font-medium leading-tight line-clamp-3 hover:bg-accent hover:text-accent-foreground transition-colors"
				>
					{anime.title}
				</Link>
			</TooltipTrigger>
			<TooltipContent
				side="right"
				sideOffset={6}
				className="p-1 bg-background border shadow-lg max-w-none"
			>
				<img
					src={anime.poster}
					alt={anime.title}
					loading="lazy"
					className="w-32 aspect-[2/3] object-cover rounded-sm"
				/>
			</TooltipContent>
		</Tooltip>
	);
}

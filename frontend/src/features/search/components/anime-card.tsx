import { Link } from "@tanstack/react-router";
import { Bookmark, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger,
} from "@/components/ui/tooltip";
import { useToggleSaved } from "@/hooks/use-toggle-saved";
import { cn } from "@/lib/utils";
import type { AnimeInfo } from "../types";

interface AnimeCardProps {
	anime: AnimeInfo;
}

export function AnimeCard({ anime }: AnimeCardProps) {
	const { isSaved, isPending, toggle } = useToggleSaved({
		id: anime.id,
		title: anime.title,
		initialSaved: anime.isSaved,
	});

	return (
		<Link
			to="/anime/$slug"
			params={{ slug: anime.id }}
			className="flex flex-col gap-2 group"
		>
			<div className="relative aspect-[2/3] w-full overflow-hidden rounded-md">
				<img
					src={anime.poster}
					alt={anime.title}
					loading="lazy"
					className="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"
				/>
				<Tooltip>
					<TooltipTrigger asChild>
						<button
							type="button"
							disabled={isPending}
							onClick={(e) => {
								e.preventDefault();
								e.stopPropagation();
								toggle();
							}}
							className="absolute top-2 right-2 p-1 rounded-md bg-background/60 backdrop-blur-sm hover:bg-background/80 transition-colors"
						>
							{isPending ? (
								<Loader2 className="size-5 animate-spin" />
							) : (
								<Bookmark
									className={cn(
										"size-5",
										isSaved && "fill-current text-indigo-500",
									)}
								/>
							)}
						</button>
					</TooltipTrigger>
					<TooltipContent>
						{isSaved ? "Remove from saved" : "Save"}
					</TooltipContent>
				</Tooltip>
			</div>
			<div className="flex flex-col gap-1 px-0.5">
				<span className="text-sm font-medium leading-tight line-clamp-2">
					{anime.title}
				</span>
				<Badge variant="secondary" className="w-fit text-xs">
					{anime.type}
				</Badge>
			</div>
		</Link>
	);
}

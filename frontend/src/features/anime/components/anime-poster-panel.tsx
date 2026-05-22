import { Bookmark, Loader2 } from "lucide-react";
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger,
} from "@/components/ui/tooltip";
import { useToggleSaved } from "@/hooks/use-toggle-saved";
import { cn } from "@/lib/utils";
import type { AnimeDetail, EpisodeInfo } from "../types";

interface AnimePosterPanelProps {
	anime: AnimeDetail;
	episodes: EpisodeInfo[];
}

export function AnimePosterPanel({ anime, episodes }: AnimePosterPanelProps) {
	const { isSaved, isPending, toggle } = useToggleSaved({
		id: anime.id,
		title: anime.title,
		initialSaved: anime.isSaved,
	});

	return (
		<div className="flex flex-col gap-4">
			{/* Poster image with bookmark overlay */}
			<div className="relative aspect-2/3 w-full overflow-hidden rounded-md">
				<img
					src={anime.poster}
					alt={anime.title}
					loading="lazy"
					className="w-full h-full object-cover"
				/>
				<Tooltip>
					<TooltipTrigger asChild>
						<button
							type="button"
							disabled={isPending}
							onClick={toggle}
							className="absolute top-1 right-1 p-1.5 rounded-md bg-background/60 backdrop-blur-sm hover:bg-background/80 transition-colors"
						>
							{isPending ? (
								<Loader2 className="size-6 animate-spin" />
							) : (
								<Bookmark
									className={cn(
										"size-6",
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

			{/* Status block — full width, large text */}
			{anime.isFinished ? (
				<div className="w-full rounded-md bg-destructive/60 text-white flex items-center justify-center py-3 text-xl font-bold">
					Finished
				</div>
			) : (
				<div className="w-full rounded-md bg-green-600 text-white flex items-center justify-center py-4 text-xl font-bold">
					In Emission
				</div>
			)}

			{/* Episode stats — single row */}
			{episodes.length > 0 && (
				<div className="grid grid-cols-3 gap-1.5">
					<div className="rounded-lg border bg-card py-2 flex flex-col items-center gap-0.5">
						<span className="text-base font-bold">{episodes.length}</span>
						<span className="text-[9px] text-muted-foreground uppercase tracking-wide">
							Total
						</span>
					</div>
					<div className="rounded-lg border bg-card py-2 flex flex-col items-center gap-0.5">
						<span className="text-base font-bold text-green-500">
							{episodes.filter((e) => e.isUserDownloaded).length}
						</span>
						<span className="text-[9px] text-muted-foreground uppercase tracking-wide">
							Download
						</span>
					</div>
					<div className="rounded-lg border bg-card py-2 flex flex-col items-center gap-0.5">
						<span className="text-base font-bold">—</span>
						<span className="text-[9px] text-muted-foreground uppercase tracking-wide">
							Storage
						</span>
					</div>
				</div>
			)}

			{/* Emission day */}
			{!anime.isFinished && anime.weekDay && (
				<p className="text-sm text-muted-foreground">Airs on {anime.weekDay}</p>
			)}

		</div>
	);
}

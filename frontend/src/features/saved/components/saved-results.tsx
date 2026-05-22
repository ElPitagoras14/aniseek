import { AnimeCard } from "@/features/search/components/anime-card";
import { Skeleton } from "@/components/ui/skeleton";
import type { SavedAnime } from "../types";

interface SavedResultsProps {
	data: SavedAnime[] | undefined;
	isLoading: boolean;
	isError: boolean;
	error: Error | null;
	hasFilters: boolean;
}

export function SavedResults({
	data,
	isLoading,
	isError,
	error,
	hasFilters,
}: SavedResultsProps) {
	if (isLoading) {
		return (
			<div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
				{Array.from({ length: 12 }).map((_, i) => (
					// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton list
					<div key={i} className="flex flex-col gap-2">
						<Skeleton className="aspect-[2/3] w-full rounded-md" />
						<Skeleton className="h-4 w-3/4" />
						<Skeleton className="h-4 w-1/3" />
					</div>
				))}
			</div>
		);
	}

	if (isError) {
		return (
			<p className="text-destructive text-sm">
				{error?.message ?? "Could not load saved animes"}
			</p>
		);
	}

	if (!data || data.length === 0) {
		return (
			<p className="text-muted-foreground text-sm">
				{hasFilters
					? "No saved animes match the current filters."
					: "You haven't saved any anime yet. Find one in Search and bookmark it."}
			</p>
		);
	}

	return (
		<div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
			{data.map((anime) => (
				<AnimeCard key={anime.id} anime={anime} />
			))}
		</div>
	);
}

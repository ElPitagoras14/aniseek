import { Skeleton } from "@/components/ui/skeleton";
import type { AnimeInfo } from "../types";
import { AnimeCard } from "./anime-card";

interface SearchResultsProps {
	query: string;
	data: AnimeInfo[] | undefined;
	isLoading: boolean;
	isError: boolean;
	error: Error | null;
}

export function SearchResults({
	query,
	data,
	isLoading,
	isError,
	error,
}: SearchResultsProps) {
	if (!query) return null;

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
				{error?.message ?? "Search failed"}
			</p>
		);
	}

	if (!data || data.length === 0) {
		return (
			<p className="text-muted-foreground text-sm">No results for "{query}".</p>
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

import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { animeDetailQueryOptions } from "@/features/anime/api";
import { AnimeDetailSkeleton } from "@/features/anime/components/anime-detail-skeleton";
import { AnimeHeader } from "@/features/anime/components/anime-header";
import { AnimePosterPanel } from "@/features/anime/components/anime-poster-panel";
import { EpisodesTab } from "@/features/anime/components/episodes-tab";
import { InfoTab } from "@/features/anime/components/info-tab";

export const Route = createFileRoute("/_app/anime/$slug")({
	component: AnimeDetailPage,
});

function AnimeDetailPage() {
	const { slug } = Route.useParams();
	const {
		data: anime,
		isLoading,
		isError,
		error,
	} = useQuery(animeDetailQueryOptions(slug));

	if (isLoading) {
		return (
			<div className="px-8 py-6 md:px-12 md:py-8">
				<AnimeDetailSkeleton />
			</div>
		);
	}

	if (isError || !anime) {
		return (
			<div className="px-8 py-6 md:px-12 md:py-8">
				<p className="text-sm text-destructive">
					{error instanceof Error ? error.message : "Failed to load anime."}
				</p>
			</div>
		);
	}

	return (
		<div className="px-6 py-6 md:px-10 md:py-8">
			<div className="grid grid-cols-1 md:grid-cols-4 gap-8 md:gap-12">
				{/* Left column: 1 unit */}
				<div>
					<AnimePosterPanel anime={anime} episodes={anime.episodes} />
				</div>
				{/* Right column: 3 units */}
				<div className="md:col-span-3 flex flex-col gap-3">
					<AnimeHeader anime={anime} />
					<Tabs defaultValue="information">
						<TabsList className="h-auto py-4.5">
							<TabsTrigger
								value="information"
								className=" px-14 py-3.5"
							>
								Information
							</TabsTrigger>
							<TabsTrigger value="episodes" className=" px-14 py-3.5">
								Episodes
							</TabsTrigger>
						</TabsList>
						<TabsContent value="information" className="mt-1">
							<InfoTab anime={anime} />
						</TabsContent>
						<TabsContent value="episodes" className="mt-2">
							<EpisodesTab
								animeId={anime.id}
								platform={anime.platform}
								episodes={anime.episodes}
							/>
						</TabsContent>
					</Tabs>
				</div>
			</div>
		</div>
	);
}

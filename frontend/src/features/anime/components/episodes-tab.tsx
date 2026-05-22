import { useState } from "react";
import type { EpisodeInfo } from "@/features/anime/types";
import { EpisodesDownloadForm } from "./episodes-download-form";
import { EpisodesTable } from "./episodes-table";

interface EpisodesTabProps {
	animeId: string;
	platform: string;
	episodes: EpisodeInfo[];
}

export function EpisodesTab({ animeId, platform, episodes }: EpisodesTabProps) {
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

	const toggleSort = () => setSortOrder((o) => (o === "asc" ? "desc" : "asc"));

	return (
		<div className="flex flex-col gap-4">
			{episodes.length > 0 && (
				<EpisodesDownloadForm
					animeId={animeId}
					maxEpisode={episodes.length}
					sortOrder={sortOrder}
					onToggleSort={toggleSort}
				/>
			)}
			<EpisodesTable
				animeId={animeId}
				platform={platform}
				episodes={episodes}
				sortOrder={sortOrder}
			/>
		</div>
	);
}

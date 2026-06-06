import type {
	EpisodeDownload,
	EpisodeDownloadList,
} from "@/features/downloads/types";

export interface Statistics {
	savedAnimes: number;
	downloadedEpisodes: number;
	inEmissionAnimes: number;
}

export type { EpisodeDownload, EpisodeDownloadList };

import type {
	EpisodeDownload,
	EpisodeDownloadList,
} from "@/features/downloads/types";

export interface Statistics {
	savedAnimes: number;
	downloadedEpisodes: number;
	inEmissionAnimes: number;
}

export interface StorageItem {
	id: string;
	title: string;
	size: number;
}

export interface StorageResponse {
	items: StorageItem[];
	total: number;
	totalSize: number;
}

export type { EpisodeDownload, EpisodeDownloadList };

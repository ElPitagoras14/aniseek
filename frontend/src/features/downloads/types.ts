export type DownloadStatus =
	| "PENDING"
	| "GETTING-LINK"
	| "DOWNLOADING"
	| "SUCCESS"
	| "FAILED"
	| "RETRYING";

export interface EpisodeDownload {
	id: number;
	animeId: string;
	title: string;
	episodeNumber: number;
	poster: string;
	jobId: string | null;
	size: number | null;
	status: DownloadStatus;
	downloadedAt: string | null;
}

export interface EpisodeDownloadList {
	items: EpisodeDownload[];
	total: number;
}

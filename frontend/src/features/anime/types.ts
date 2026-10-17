export interface RelatedInfo {
	id: string;
	title: string;
	type: string;
}

export interface EpisodeInfo {
	id: number;
	animeId: string;
	url: string;
	imagePreview: string;
	isUserDownloaded: boolean;
	isGlobalDownloaded: boolean;
}

export interface AnimeDetail {
	id: string;
	title: string;
	type: string;
	poster: string;
	isSaved: boolean;
	saveDate: string | null;
	season: number | null;
	description: string;
	genres: string[];
	relatedInfo: RelatedInfo[];
	weekDay: string | null;
	episodes: EpisodeInfo[];
	isFinished: boolean;
	lastScrapedAt: string | null;
}

export interface ApiEnvelope<T> {
	status: string;
	message: string;
	payload: T;
	statusCode: number;
}

export interface BulkDownloadItem {
	jobId: string | null;
	episodeNumber: number;
	success: boolean;
	// Why the episode was not enqueued; null when it was.
	reason: "already_downloaded" | "not_found" | "enqueue_failed" | null;
}

export interface BulkDownloadResult {
	items: BulkDownloadItem[];
	total: number;
}

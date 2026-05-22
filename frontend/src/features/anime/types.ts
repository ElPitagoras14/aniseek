export interface RelatedInfo {
	id: string;
	title: string;
	type: string;
}

export interface EpisodeInfo {
	id: number;
	animeId: string;
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
	platform: string;
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
}

export interface BulkDownloadResult {
	items: BulkDownloadItem[];
	total: number;
}

export interface AnimeInfo {
	id: string;
	title: string;
	type: string;
	poster: string;
	isSaved: boolean;
	saveDate: string | null;
}

export interface SearchResponse {
	status: string;
	message: string;
	payload: { items: AnimeInfo[]; total: number };
	statusCode: number;
}

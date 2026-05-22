import type { AnimeInfo } from "@/features/search/types";

export interface SavedAnime extends AnimeInfo {
	isFinished: boolean;
}

export interface SavedAnimesResponse {
	status: string;
	message: string;
	payload: { items: SavedAnime[]; total: number };
	statusCode: number;
}

export type SortField = "title" | "saveDate";
export type SortOrder = "asc" | "desc";
export type StatusFilter = "all" | "airing" | "finished";

export interface SortOption {
	field: SortField;
	order: SortOrder;
}

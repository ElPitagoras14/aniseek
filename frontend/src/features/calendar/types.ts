import type { ApiEnvelope } from "@/features/anime/types";
import type { AnimeInfo } from "@/features/search/types";

export type WeekDay =
	| "Monday"
	| "Tuesday"
	| "Wednesday"
	| "Thursday"
	| "Friday"
	| "Saturday"
	| "Sunday";

export interface InEmissionAnime extends AnimeInfo {
	weekDay: WeekDay;
}

export interface InEmissionList {
	items: InEmissionAnime[];
	total: number;
}

export type InEmissionResponse = ApiEnvelope<InEmissionList>;

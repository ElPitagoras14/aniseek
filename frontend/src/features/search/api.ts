import type { QueryFunctionContext } from "@tanstack/react-query";
import { api } from "@/api";
import type { AnimeInfo, SearchResponse } from "./types";

type SearchKey = readonly ["animes", "search", string];

export const searchAnimes = async ({
	queryKey,
}: QueryFunctionContext<SearchKey>): Promise<AnimeInfo[]> => {
	const [, , query] = queryKey;
	const { data } = await api.get<SearchResponse>("/animes/search", {
		params: { query },
	});
	return data.payload.items;
};

export const saveAnime = (id: string) => api.put(`/animes/${id}/save`);
export const unsaveAnime = (id: string) => api.put(`/animes/${id}/unsave`);

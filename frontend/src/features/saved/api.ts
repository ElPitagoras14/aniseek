import { queryOptions } from "@tanstack/react-query";
import { api } from "@/api";
import type { SavedAnime, SavedAnimesResponse } from "./types";

export const fetchSavedAnimes = async (): Promise<SavedAnime[]> => {
	const { data } = await api.get<SavedAnimesResponse>("/animes/saved");
	return data.payload.items;
};

export const savedAnimesQueryOptions = queryOptions({
	queryKey: ["animes", "saved"] as const,
	queryFn: fetchSavedAnimes,
	staleTime: 0,
});

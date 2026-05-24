import { queryOptions } from "@tanstack/react-query";
import { api } from "@/api";
import type { InEmissionAnime, InEmissionResponse } from "./types";

export const fetchInEmissionAnimes = async (): Promise<InEmissionAnime[]> => {
	const { data } = await api.get<InEmissionResponse>("/animes/in-emission");
	return data.payload.items;
};

export const inEmissionQueryOptions = queryOptions({
	queryKey: ["animes", "in-emission"] as const,
	queryFn: fetchInEmissionAnimes,
	staleTime: 60_000,
});

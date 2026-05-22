import type { QueryFunctionContext } from "@tanstack/react-query";
import { queryOptions } from "@tanstack/react-query";
import { api } from "@/api";
import type { AnimeDetail, ApiEnvelope, BulkDownloadResult } from "./types";

type AnimeDetailKey = readonly ["animes", "detail", string];

const fetchAnimeDetail = async ({
	queryKey,
}: QueryFunctionContext<AnimeDetailKey>): Promise<AnimeDetail> => {
	const [, , id] = queryKey;
	const { data } = await api.get<ApiEnvelope<AnimeDetail>>(`/animes/${id}`);
	return data.payload;
};

export const animeDetailQueryOptions = (id: string) =>
	queryOptions({
		queryKey: ["animes", "detail", id] as const,
		queryFn: fetchAnimeDetail,
		staleTime: 60_000,
	});

export const refreshAnime = (id: string) =>
	api.put<ApiEnvelope<AnimeDetail>>(`/animes/${id}`);

export const downloadEpisode = (animeId: string, episodeNumber: number) =>
	api.post(`/episodes/${animeId}/${episodeNumber}/download`);

export const downloadEpisodesBulk = (animeId: string, episodes: number[]) =>
	api.post<ApiEnvelope<BulkDownloadResult>>(
		`/episodes/${animeId}/download/bulk`,
		episodes,
	);

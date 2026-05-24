import type { QueryFunctionContext } from "@tanstack/react-query";
import { queryOptions } from "@tanstack/react-query";
import { api } from "@/api";
import type { ApiEnvelope } from "@/features/anime/types";
import type { EpisodeDownloadList } from "./types";

const VITE_API_URL = import.meta.env.VITE_API_URL;

interface DownloadsQueryParams {
	q: string;
	page: number;
	limit: number;
}

type DownloadsQueryKey = readonly [
	"episodes",
	"downloads",
	DownloadsQueryParams,
];

const fetchDownloads = async ({
	queryKey,
}: QueryFunctionContext<DownloadsQueryKey>): Promise<EpisodeDownloadList> => {
	const [, , { q, page, limit }] = queryKey;
	const params = new URLSearchParams({
		page: String(page),
		limit: String(limit),
	});
	if (q) params.set("q", q);
	const { data } = await api.get<ApiEnvelope<EpisodeDownloadList>>(
		`/episodes/downloads?${params}`,
	);
	return data.payload;
};

export const downloadsQueryOptions = ({
	q,
	page,
	limit,
}: DownloadsQueryParams) =>
	queryOptions({
		queryKey: ["episodes", "downloads", { q, page, limit }] as const,
		queryFn: fetchDownloads,
		staleTime: 0,
	});

export const deleteEpisodeDownload = (animeId: string, episodeNumber: number) =>
	api.delete(`/episodes/${animeId}/${episodeNumber}/download`);

export const retryEpisodeDownload = (animeId: string, episodeNumber: number) =>
	api.post(
		`/episodes/${animeId}/${episodeNumber}/download?force_download=true`,
	);

export const episodeFileUrl = (
	animeId: string,
	episodeNumber: number,
): string => `${VITE_API_URL}/api/episodes/${animeId}/${episodeNumber}/file`;

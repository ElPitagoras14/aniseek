import { queryOptions } from "@tanstack/react-query";
import { api } from "@/api";
import type { ApiEnvelope } from "@/features/anime/types";
import type { EpisodeDownloadList } from "@/features/downloads/types";
import type { Statistics, StorageResponse } from "./types";

const fetchStatistics = async (): Promise<Statistics> => {
	const { data } = await api.get<ApiEnvelope<Statistics>>("/users/statistics");
	return data.payload;
};

export const statisticsQueryOptions = queryOptions({
	queryKey: ["users", "statistics"] as const,
	queryFn: fetchStatistics,
	staleTime: 60_000,
});

const fetchDownloadsLast = async (): Promise<EpisodeDownloadList> => {
	const { data } = await api.get<ApiEnvelope<EpisodeDownloadList>>(
		"/episodes/downloads/last",
	);
	return data.payload;
};

export const downloadsLastQueryOptions = queryOptions({
	queryKey: ["episodes", "downloads", "last"] as const,
	queryFn: fetchDownloadsLast,
	staleTime: 0,
});

interface StorageQueryParams {
	page: number;
	limit: number;
}

const fetchStorage = async ({
	page,
	limit,
}: StorageQueryParams): Promise<StorageResponse> => {
	const params = new URLSearchParams({
		page: String(page),
		limit: String(limit),
	});
	const { data } = await api.get<ApiEnvelope<StorageResponse>>(
		`/episodes/storage?${params}`,
	);
	return data.payload;
};

export const storageQueryOptions = ({ page, limit }: StorageQueryParams) =>
	queryOptions({
		queryKey: ["episodes", "storage", { page, limit }] as const,
		queryFn: () => fetchStorage({ page, limit }),
		staleTime: 60_000,
	});

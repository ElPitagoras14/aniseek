import { queryOptions } from "@tanstack/react-query";
import { api } from "@/api";
import type { ApiEnvelope } from "@/features/anime/types";
import type { EpisodeDownloadList } from "@/features/downloads/types";
import type { Statistics } from "./types";

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

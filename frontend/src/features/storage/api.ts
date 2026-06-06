import { queryOptions } from "@tanstack/react-query";
import { api } from "@/api";
import type { ApiEnvelope } from "@/features/anime/types";
import type { StorageResponse } from "./types";

export const deleteAnimeStorage = async (animeId: string): Promise<void> => {
	await api.delete(`/episodes/storage/${animeId}`);
};

interface StorageQueryParams {
	q?: string;
	page: number;
	limit: number;
}

const fetchStorage = async ({
	q,
	page,
	limit,
}: StorageQueryParams): Promise<StorageResponse> => {
	const params = new URLSearchParams({
		page: String(page),
		limit: String(limit),
	});
	if (q) params.set("q", q);
	const { data } = await api.get<ApiEnvelope<StorageResponse>>(
		`/episodes/storage?${params}`,
	);
	return data.payload;
};

export const storageQueryOptions = ({ q, page, limit }: StorageQueryParams) =>
	queryOptions({
		queryKey: ["episodes", "storage", { q, page, limit }] as const,
		queryFn: () => fetchStorage({ q, page, limit }),
		staleTime: 60_000,
	});

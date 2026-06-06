import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { statisticsQueryOptions } from "@/features/home/api";
import { storageQueryOptions } from "@/features/storage/api";
import { StorageKpis } from "@/features/storage/components/storage-kpis";
import { StorageSearchInput } from "@/features/storage/components/storage-search-input";
import { StorageTable } from "@/features/storage/components/storage-table";

const VALID_LIMITS = [5, 10, 20, 50] as const;
type PageLimit = (typeof VALID_LIMITS)[number];

export const Route = createFileRoute("/_app/storage")({
	validateSearch: (s): { q: string; page: number; limit: PageLimit } => ({
		q: typeof s.q === "string" ? s.q : "",
		page: typeof s.page === "number" && s.page > 0 ? s.page : 1,
		limit: VALID_LIMITS.includes(s.limit as PageLimit)
			? (s.limit as PageLimit)
			: 10,
	}),
	component: RouteComponent,
});

function RouteComponent() {
	const { q, page, limit } = Route.useSearch();
	const navigate = Route.useNavigate();

	const storage = useQuery(storageQueryOptions({ q, page, limit }));
	const statistics = useQuery(statisticsQueryOptions);

	return (
		<div className="p-4 md:p-6 flex flex-col gap-6">
			<div className="flex flex-col gap-4">
				<h1 className="text-2xl font-semibold">Storage</h1>
				<StorageKpis
					storageTotal={storage.data?.totalSize}
					storageCount={storage.data?.total}
					episodesDownloaded={statistics.data?.downloadedEpisodes}
					isStorageLoading={storage.isLoading}
					isStorageError={storage.isError}
					isStatsLoading={statistics.isLoading}
					isStatsError={statistics.isError}
				/>
				<StorageSearchInput
					defaultValue={q}
					onDebouncedChange={(next) =>
						navigate({ search: { q: next, page: 1, limit } })
					}
				/>
			</div>
			<StorageTable
				data={storage.data}
				isLoading={storage.isLoading}
				isError={storage.isError}
				refetch={() => storage.refetch()}
				page={page}
				limit={limit}
				onPageChange={(p) => navigate({ search: { q, page: p, limit } })}
				onLimitChange={(l) =>
					navigate({ search: { q, page: 1, limit: l as PageLimit } })
				}
			/>
		</div>
	);
}

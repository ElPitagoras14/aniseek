import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { savedAnimesQueryOptions } from "@/features/saved/api";
import { SavedFilters } from "@/features/saved/components/saved-filters";
import { SavedHeader } from "@/features/saved/components/saved-header";
import { SavedResults } from "@/features/saved/components/saved-results";
import type { SortOption, StatusFilter } from "@/features/saved/types";

export const Route = createFileRoute("/_app/saved")({
	component: SavedPage,
});

const DEFAULT_SORT: SortOption = { field: "saveDate", order: "desc" };

function SavedPage() {
	const { data, isLoading, isError, error } = useQuery(savedAnimesQueryOptions);

	const [search, setSearch] = useState("");
	const [sort, setSort] = useState<SortOption>(DEFAULT_SORT);
	const [status, setStatus] = useState<StatusFilter>("all");

	const displayed = useMemo(() => {
		if (!data) return undefined;
		const term = search.trim().toLowerCase();

		const filtered = data.filter((a) => {
			if (term && !a.title.toLowerCase().includes(term)) return false;
			if (status === "airing" && a.isFinished) return false;
			if (status === "finished" && !a.isFinished) return false;
			return true;
		});

		const sorted = [...filtered].sort((a, b) => {
			if (sort.field === "title") {
				return a.title.localeCompare(b.title);
			}
			const aTime = a.saveDate ? new Date(a.saveDate).getTime() : 0;
			const bTime = b.saveDate ? new Date(b.saveDate).getTime() : 0;
			return aTime - bTime;
		});

		if (sort.order === "desc") sorted.reverse();
		return sorted;
	}, [data, search, sort, status]);

	const hasFilters = search.trim().length > 0 || status !== "all";

	return (
		<div className="p-4 md:p-6 flex flex-col gap-6">
			<SavedHeader count={data?.length} isLoading={isLoading} />
			<SavedFilters
				search={search}
				onSearchChange={setSearch}
				sort={sort}
				onSortChange={setSort}
				status={status}
				onStatusChange={setStatus}
			/>
			<SavedResults
				data={displayed}
				isLoading={isLoading}
				isError={isError}
				error={error}
				hasFilters={hasFilters}
			/>
		</div>
	);
}

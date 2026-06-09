import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { savedAnimesQueryOptions } from "@/features/saved/api";
import { SavedFilters } from "@/features/saved/components/saved-filters";
import { SavedHeader } from "@/features/saved/components/saved-header";
import { SavedResults } from "@/features/saved/components/saved-results";
import type { SavedAnime, SortOption, StatusFilter } from "@/features/saved/types";

export const Route = createFileRoute("/_app/saved")({
	component: SavedPage,
});

const DEFAULT_SORT: SortOption = { field: "saveDate", order: "desc" };

function SavedPage() {
	const { data, isLoading, isError, error } = useQuery(savedAnimesQueryOptions);

	const [search, setSearch] = useState("");
	const [sort, setSort] = useState<SortOption>(DEFAULT_SORT);
	const [status, setStatus] = useState<StatusFilter>("all");
	const [stableData, setStableData] = useState<SavedAnime[] | undefined>(undefined);

	useEffect(() => {
		if (!data) return;
		setStableData((prev) => {
			if (!prev) return data;
			const freshMap = new Map(data.map((a) => [a.id, a]));
			const updated = prev.map((a) => freshMap.get(a.id) ?? a);
			const added = data.filter((a) => !prev.some((p) => p.id === a.id));
			return [...updated, ...added];
		});
	}, [data]);

	const displayed = useMemo(() => {
		if (!stableData) return undefined;
		const term = search.trim().toLowerCase();

		const filtered = stableData.filter((a) => {
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
	}, [stableData, search, sort, status]);

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

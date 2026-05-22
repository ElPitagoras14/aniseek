import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { searchAnimes } from "@/features/search/api";
import { SearchForm } from "@/features/search/components/search-form";
import { SearchResults } from "@/features/search/components/search-results";

export const Route = createFileRoute("/_app/search")({
	validateSearch: (search): { query: string } => ({
		query: typeof search.query === "string" ? search.query : "",
	}),
	component: SearchPage,
});

function SearchPage() {
	const { query } = Route.useSearch();
	const navigate = Route.useNavigate();

	const { data, isLoading, isError, error } = useQuery({
		queryKey: ["animes", "search", query] as const,
		queryFn: searchAnimes,
		enabled: query.trim().length > 0,
		staleTime: 60_000,
	});

	const subtitle = (() => {
		if (!query) return "Search among thousands of animes";
		if (isLoading) return "Searching...";
		if (isError) return "Search could not be completed";
		if (!data || data.length === 0) return `No results for "${query}"`;
		return `${data.length} anime${data.length !== 1 ? "s" : ""} found`;
	})();

	return (
		<div className="p-4 md:p-6 flex flex-col gap-6">
			<div className="flex flex-col gap-1">
				<h1 className="text-2xl font-semibold">Search</h1>
				<p className="text-sm text-muted-foreground">{subtitle}</p>
			</div>
			<SearchForm
				defaultValue={query}
				onSubmit={(q) => navigate({ search: { query: q } })}
			/>
			<SearchResults
				query={query}
				data={data}
				isLoading={isLoading}
				isError={isError}
				error={error}
			/>
		</div>
	);
}

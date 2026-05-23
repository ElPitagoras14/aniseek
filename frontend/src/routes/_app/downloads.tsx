import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { downloadsQueryOptions } from "@/features/downloads/api";
import { DownloadsHeader } from "@/features/downloads/components/downloads-header";
import { DownloadsList } from "@/features/downloads/components/downloads-list";
import { useDownloadProgress } from "@/features/downloads/hooks/use-download-progress";

const VALID_LIMITS = [5, 10, 20, 50] as const;
type PageLimit = (typeof VALID_LIMITS)[number];

const ACTIVE_STATES = new Set<string>([
	"PENDING",
	"GETTING-LINK",
	"DOWNLOADING",
	"RETRYING",
]);

export const Route = createFileRoute("/_app/downloads")({
	validateSearch: (s): { q: string; page: number; limit: PageLimit } => ({
		q: typeof s.q === "string" ? s.q : "",
		page: typeof s.page === "number" && s.page > 0 ? s.page : 1,
		limit: VALID_LIMITS.includes(s.limit as PageLimit)
			? (s.limit as PageLimit)
			: 10,
	}),
	component: DownloadsPage,
});

function DownloadsPage() {
	const { q, page, limit } = Route.useSearch();
	const navigate = Route.useNavigate();

	const { data, isLoading, isError, error } = useQuery(
		downloadsQueryOptions({ q, page, limit }),
	);

	const activeJobIds = (data?.items ?? [])
		.filter((d) => d.jobId != null && ACTIVE_STATES.has(d.status))
		.map((d) => d.jobId as string);

	const progressMap = useDownloadProgress(activeJobIds);

	return (
		<div className="p-4 md:p-6 flex flex-col gap-6">
			<DownloadsHeader
				defaultValue={q}
				onSearch={(next) => navigate({ search: { q: next, page: 1, limit } })}
			/>
			<DownloadsList
				data={data}
				isLoading={isLoading}
				isError={isError}
				error={error}
				progressMap={progressMap}
				page={page}
				limit={limit}
				onPageChange={(p) => navigate({ search: { q, page: p, limit } })}
				onLimitChange={(l) =>
					navigate({ search: { q, page: 1, limit: l as PageLimit } })
				}
				q={q}
			/>
		</div>
	);
}

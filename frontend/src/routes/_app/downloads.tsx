import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { downloadsQueryOptions } from "@/features/downloads/api";
import { DownloadsHeader } from "@/features/downloads/components/downloads-header";
import { DownloadsList } from "@/features/downloads/components/downloads-list";
import { useDownloadProgress } from "@/features/downloads/hooks/use-download-progress";

const PAGE_SIZE = 10;
const ACTIVE_STATES = new Set<string>([
	"PENDING",
	"GETTING-LINK",
	"DOWNLOADING",
	"RETRYING",
]);

export const Route = createFileRoute("/_app/downloads")({
	validateSearch: (s): { q: string; page: number } => ({
		q: typeof s.q === "string" ? s.q : "",
		page: typeof s.page === "number" && s.page > 0 ? s.page : 1,
	}),
	component: DownloadsPage,
});

function DownloadsPage() {
	const { q, page } = Route.useSearch();
	const navigate = Route.useNavigate();

	const { data, isLoading, isError, error } = useQuery(
		downloadsQueryOptions({ q, page, limit: PAGE_SIZE }),
	);

	const activeJobIds = (data?.items ?? [])
		.filter((d) => d.jobId != null && ACTIVE_STATES.has(d.status))
		.map((d) => d.jobId as string);

	const progressMap = useDownloadProgress(activeJobIds);

	return (
		<div className="p-4 md:p-6 flex flex-col gap-6">
			<DownloadsHeader
				defaultValue={q}
				onSearch={(next) => navigate({ search: { q: next, page: 1 } })}
			/>
			<DownloadsList
				data={data}
				isLoading={isLoading}
				isError={isError}
				error={error}
				progressMap={progressMap}
				page={page}
				limit={PAGE_SIZE}
				onPageChange={(p) => navigate({ search: { q, page: p } })}
				q={q}
			/>
		</div>
	);
}

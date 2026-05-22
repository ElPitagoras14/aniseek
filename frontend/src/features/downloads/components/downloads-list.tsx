import type { DownloadProgress } from "../hooks/use-download-progress";
import type { EpisodeDownloadList } from "../types";
import { DownloadRow } from "./download-row";
import { DownloadRowSkeleton } from "./download-row-skeleton";
import { DownloadsPagination } from "./downloads-pagination";

interface DownloadsListProps {
	data: EpisodeDownloadList | undefined;
	isLoading: boolean;
	isError: boolean;
	error: Error | null;
	progressMap: Record<string, DownloadProgress>;
	page: number;
	limit: number;
	onPageChange: (page: number) => void;
	q: string;
}

export function DownloadsList({
	data,
	isLoading,
	isError,
	error,
	progressMap,
	page,
	limit,
	onPageChange,
	q,
}: DownloadsListProps) {
	if (isLoading) {
		return (
			<div className="border rounded-lg overflow-hidden">
				{Array.from({ length: 5 }).map((_, i) => (
					// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton list
					<DownloadRowSkeleton key={i} />
				))}
			</div>
		);
	}

	if (isError) {
		return (
			<p className="text-destructive text-sm">
				{error?.message ?? "Error al cargar las descargas"}
			</p>
		);
	}

	if (!data) {
		return <p className="text-muted-foreground text-sm">No hay descargas.</p>;
	}

	if (data.items.length === 0) {
		return (
			<p className="text-muted-foreground text-sm">
				{q ? "No hay descargas que coincidan." : "No hay descargas."}
			</p>
		);
	}

	return (
		<div className="flex flex-col">
			<div className="border rounded-lg overflow-hidden">
				{data.items.map((item) => (
					<DownloadRow
						key={item.id}
						item={item}
						progress={item.jobId ? progressMap[item.jobId] : undefined}
					/>
				))}
			</div>
			<DownloadsPagination
				page={page}
				total={data.total}
				limit={limit}
				onPageChange={onPageChange}
			/>
		</div>
	);
}

import { Film, HardDrive, Download } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatBytes } from "@/lib/format-bytes";

interface StorageKpisProps {
	storageTotal: number | undefined; // totalSize from StorageResponse
	storageCount: number | undefined; // total from StorageResponse
	episodesDownloaded: number | undefined; // downloadedEpisodes from Statistics
	isStorageLoading: boolean;
	isStorageError: boolean;
	isStatsLoading: boolean;
	isStatsError: boolean;
}

export function StorageKpis({
	storageTotal,
	storageCount,
	episodesDownloaded,
	isStorageLoading,
	isStorageError,
	isStatsLoading,
	isStatsError,
}: StorageKpisProps) {
	return (
		<div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
			<Card>
				<CardContent className="flex flex-col gap-3">
					<div className="flex items-center gap-2">
						<HardDrive className="size-4 text-violet-500" />
						<span className="text-xs uppercase tracking-wide text-muted-foreground">
							Total storage
						</span>
					</div>
					{isStorageError ? (
						<span className="text-sm text-destructive">—</span>
					) : isStorageLoading ? (
						<Skeleton className="h-9 w-20" />
					) : (
						<span className="text-3xl font-bold">
							{formatBytes(storageTotal ?? 0)}
						</span>
					)}
				</CardContent>
			</Card>

			<Card>
				<CardContent className="flex flex-col gap-3">
					<div className="flex items-center gap-2">
						<Film className="size-4 text-sky-500" />
						<span className="text-xs uppercase tracking-wide text-muted-foreground">
							Animes
						</span>
					</div>
					{isStorageError ? (
						<span className="text-sm text-destructive">—</span>
					) : isStorageLoading ? (
						<Skeleton className="h-9 w-20" />
					) : (
						<span className="text-3xl font-bold">{storageCount}</span>
					)}
				</CardContent>
			</Card>

			<Card>
				<CardContent className="flex flex-col gap-3">
					<div className="flex items-center gap-2">
						<Download className="size-4 text-emerald-500" />
						<span className="text-xs uppercase tracking-wide text-muted-foreground">
							Episodes downloaded
						</span>
					</div>
					{isStatsError ? (
						<span className="text-sm text-destructive">—</span>
					) : isStatsLoading ? (
						<Skeleton className="h-9 w-20" />
					) : (
						<span className="text-3xl font-bold">{episodesDownloaded}</span>
					)}
				</CardContent>
			</Card>
		</div>
	);
}

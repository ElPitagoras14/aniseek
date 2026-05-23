import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { formatBytes } from "@/lib/format-bytes";
import { episodeFileUrl } from "../api";
import type { DownloadProgress } from "../hooks/use-download-progress";
import type { EpisodeDownload } from "../types";
import { DownloadProgressDisplay } from "./download-progress";
import { DownloadRowActions } from "./download-row-actions";

interface DownloadRowProps {
	item: EpisodeDownload;
	progress?: DownloadProgress;
}

export const ROW_COLS = "grid-cols-[56px_1fr_120px_260px_140px_44px]";

export function DownloadRow({ item, progress }: DownloadRowProps) {
	const liveStatus = progress?.state ?? item.status;
	const meta = progress?.meta ?? {};
	const isDownloading = liveStatus === "DOWNLOADING";

	return (
		<div
			className={`grid ${ROW_COLS} items-center gap-4 px-4 py-2 border-b last:border-b-0`}
		>
			<img
				src={item.poster}
				alt={item.title}
				className="w-14 aspect-2/3 object-cover rounded"
			/>

			<div className="min-w-0 flex flex-col gap-1">
				<a
					href={`/anime/${item.animeId}`}
					className="text-sm font-medium truncate hover:underline"
				>
					{item.title}
				</a>
			</div>

			<span className="text-sm text-muted-foreground text-center">
				{item.episodeNumber}
			</span>

			<div className="flex items-center justify-center">
				{liveStatus === "SUCCESS" ? (
					<Button
						variant="ghost"
						size="icon"
						asChild
						aria-label="Descargar episodio"
					>
						<a href={episodeFileUrl(item.id)} download>
							<Download className="size-4" />
						</a>
					</Button>
				) : isDownloading ? (
					<div className="flex items-center gap-2 w-full px-2">
						<div className="h-1.5 flex-1 bg-muted rounded-full overflow-hidden">
							<div
								className="h-full bg-primary transition-all"
								style={{
									width: `${Math.min(100, Math.max(0, meta.progress ?? 0))}%`,
								}}
							/>
						</div>
						<span className="text-xs text-muted-foreground shrink-0">
							{(meta.progress ?? 0).toFixed(0)}%
						</span>
					</div>
				) : (
					<DownloadProgressDisplay status={item.status} progress={progress} />
				)}
			</div>

			<span className="text-sm text-muted-foreground text-center">
				{formatBytes(item.size)}
			</span>

			<DownloadRowActions
				animeId={item.animeId}
				episodeNumber={item.episodeNumber}
				status={liveStatus}
			/>
		</div>
	);
}

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

	const size = formatBytes(meta.size ?? item.size);

	return (
		// Below md the row is a card; the md:contents wrapper lets its children
		// become the desktop grid cells, so the desktop row is unchanged.
		<div
			className={`flex items-start gap-3 border-b px-3 py-3 last:border-b-0 md:grid ${ROW_COLS} md:items-center md:gap-4 md:px-4 md:py-2`}
		>
			<img
				src={item.poster}
				alt={item.title}
				className="aspect-2/3 w-12 shrink-0 rounded object-cover md:w-auto"
			/>

			<div className="flex min-w-0 flex-1 flex-col gap-1.5 md:contents">
				<div className="line-clamp-2 min-w-0 md:line-clamp-none">
					{item.title}
				</div>

				<span className="text-xs text-muted-foreground md:hidden">
					Ep {item.episodeNumber} · {size}
				</span>

				<span className="hidden text-center text-sm text-muted-foreground md:block">
					{item.episodeNumber}
				</span>

				<div className="flex items-center md:justify-center">
					{liveStatus === "SUCCESS" ? (
						<Button
							variant="ghost"
							size="icon"
							asChild
							aria-label="Download episode"
						>
							<a
								href={episodeFileUrl(item.animeId, item.episodeNumber)}
								download
							>
								<Download className="size-4" />
							</a>
						</Button>
					) : isDownloading ? (
						<div className="flex w-full items-center gap-2 md:px-2">
							<div className="h-2.5 flex-1 overflow-hidden rounded-full bg-muted">
								<div
									className="h-full bg-primary transition-all"
									style={{
										width: `${Math.min(100, Math.max(0, meta.progress ?? 0))}%`,
									}}
								/>
							</div>
							<span className="shrink-0 text-xs text-muted-foreground">
								{(meta.progress ?? 0).toFixed(0)}%
							</span>
						</div>
					) : (
						<DownloadProgressDisplay status={item.status} progress={progress} />
					)}
				</div>

				<span className="hidden text-center text-sm text-muted-foreground md:block">
					{size}
				</span>
			</div>

			<DownloadRowActions
				animeId={item.animeId}
				episodeNumber={item.episodeNumber}
				status={liveStatus}
			/>
		</div>
	);
}

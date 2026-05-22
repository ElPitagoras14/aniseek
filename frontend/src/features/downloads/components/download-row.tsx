import { formatBytes } from "@/lib/format-bytes";
import type { DownloadProgress } from "../hooks/use-download-progress";
import type { EpisodeDownload } from "../types";
import { DownloadProgressDisplay } from "./download-progress";
import { DownloadRowActions } from "./download-row-actions";

interface DownloadRowProps {
	item: EpisodeDownload;
	progress?: DownloadProgress;
}

export function DownloadRow({ item, progress }: DownloadRowProps) {
	return (
		<div className="flex items-start gap-3 md:gap-4 p-3 border-b last:border-b-0">
			<img
				src={item.poster}
				alt={item.title}
				className="w-16 md:w-20 aspect-[2/3] object-cover rounded-md flex-shrink-0"
			/>
			<div className="flex flex-col gap-1 flex-1 min-w-0">
				<a
					href={`/anime/${item.animeId}`}
					className="font-medium text-sm truncate hover:underline"
				>
					{item.title}
				</a>
				<p className="text-xs text-muted-foreground">
					Episodio {item.episodeNumber}
					{item.size ? ` · ${formatBytes(item.size)}` : ""}
				</p>
				<DownloadProgressDisplay
					status={item.status}
					size={item.size}
					progress={progress}
				/>
			</div>
			<DownloadRowActions
				id={item.id}
				animeId={item.animeId}
				episodeNumber={item.episodeNumber}
				status={progress?.state ?? item.status}
			/>
		</div>
	);
}

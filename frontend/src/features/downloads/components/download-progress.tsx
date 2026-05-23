import { Badge } from "@/components/ui/badge";
import type { DownloadProgress } from "../hooks/use-download-progress";
import type { DownloadStatus } from "../types";

interface DownloadProgressProps {
	status: DownloadStatus;
	progress?: DownloadProgress;
}

export function DownloadProgressDisplay({
	status,
	progress,
}: DownloadProgressProps) {
	const liveStatus = progress?.state ?? status;
	const meta = progress?.meta ?? {};

	switch (liveStatus) {
		case "GETTING-LINK":
			return (
				<Badge variant="secondary" className="text-xs px-3 py-3">
					Looking for link…
				</Badge>
			);

		case "RETRYING": {
			const attempt = meta.retry_count;
			const total = meta.max_retries;
			return (
				<Badge
					variant="outline"
					className="text-orange-600 border-orange-400 text-xs w-fit px-3 py-3"
				>
					{attempt && total ? `Retry ${attempt}/${total}` : "Retrying"}
				</Badge>
			);
		}

		case "FAILED":
			return (
				<Badge variant="destructive" className="text-xs px-3 py-3">
					Failed
				</Badge>
			);

		default:
			return (
				<Badge variant="secondary" className="text-xs px-3 py-3">
					Queued
				</Badge>
			);
	}
}

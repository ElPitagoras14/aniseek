import { Badge } from "@/components/ui/badge";
import { formatBytes } from "@/lib/format-bytes";
import type { DownloadProgress } from "../hooks/use-download-progress";
import type { DownloadStatus } from "../types";

interface DownloadProgressProps {
	status: DownloadStatus;
	progress?: DownloadProgress;
}

function ProgressBar({ value }: { value: number }) {
	return (
		<div className="h-2.5 w-full bg-muted rounded-full overflow-hidden">
			<div
				className="h-full bg-primary transition-all"
				style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
			/>
		</div>
	);
}

export function DownloadProgressDisplay({
	status,
	progress,
}: DownloadProgressProps) {
	const liveStatus = progress?.state ?? status;
	const meta = progress?.meta ?? {};

	switch (liveStatus) {
		case "SUCCESS":
			return (
				<div className="flex items-center gap-2">
					<Badge
						variant="default"
						className="bg-green-600 text-white hover:bg-green-700 text-xs"
					>
						Descargado
					</Badge>
				</div>
			);

		case "DOWNLOADING": {
			const pct = meta.progress ?? 0;
			const downloaded = meta.total ? (meta.total * pct) / 100 : null;
			return (
				<div className="flex flex-col gap-1">
					<ProgressBar value={pct} />
					<span className="text-xs text-muted-foreground">
						{pct.toFixed(0)}%
						{meta.total
							? ` · ${formatBytes(downloaded)} / ${formatBytes(meta.total)}`
							: ""}
					</span>
				</div>
			);
		}

		case "GETTING-LINK":
			return (
				<Badge variant="secondary" className="text-xs">
					Buscando enlace…
				</Badge>
			);

		case "RETRYING":
			return (
				<Badge
					variant="outline"
					className="text-orange-600 border-orange-400 text-xs w-fit"
				>
					Reintentando ({meta.retry_count ?? "?"}/{meta.max_retries ?? "?"})
				</Badge>
			);

		case "FAILED":
			return (
				<Badge variant="destructive" className="text-xs">
					Fallido
				</Badge>
			);

		default:
			return (
				<Badge variant="secondary" className="text-xs">
					En cola
				</Badge>
			);
	}
}

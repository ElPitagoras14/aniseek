import type { EpisodeInfo } from "@/features/anime/types";

interface EpisodesStatsCardProps {
	episodes: EpisodeInfo[];
}

export function EpisodesStatsCard({ episodes }: EpisodesStatsCardProps) {
	const downloaded = episodes.filter((e) => e.isUserDownloaded).length;
	const available = episodes.filter((e) => e.isGlobalDownloaded).length;

	return (
		<div className="grid grid-cols-4 gap-3">
			<div className="rounded-xl border bg-card p-5 flex flex-col items-center gap-1.5">
				<span className="text-3xl font-bold">{episodes.length}</span>
				<span className="text-xs text-muted-foreground uppercase tracking-wide">
					Total
				</span>
			</div>
			<div className="rounded-xl border bg-card p-5 flex flex-col items-center gap-1.5">
				<span className="text-3xl font-bold text-green-500">{downloaded}</span>
				<span className="text-xs text-muted-foreground uppercase tracking-wide">
					Downloaded
				</span>
			</div>
			<div className="rounded-xl border bg-card p-5 flex flex-col items-center gap-1.5">
				<span className="text-3xl font-bold text-blue-500">{available}</span>
				<span className="text-xs text-muted-foreground uppercase tracking-wide">
					Available
				</span>
			</div>
			<div className="rounded-xl border bg-card p-5 flex flex-col items-center gap-1.5">
				<span className="text-3xl font-bold">—</span>
				<span className="text-xs text-muted-foreground uppercase tracking-wide">
					Storage
				</span>
			</div>
		</div>
	);
}

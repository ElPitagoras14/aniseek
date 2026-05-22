import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useVirtualizer } from "@tanstack/react-virtual";
import type { AxiosError } from "axios";
import { CircleCheck, CircleX, Download, Play } from "lucide-react";
import { useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger,
} from "@/components/ui/tooltip";
import { downloadEpisode } from "@/features/anime/api";
import { buildEpisodeUrl } from "@/features/anime/lib/build-episode-url";
import type { EpisodeInfo } from "@/features/anime/types";

interface EpisodesTableProps {
	animeId: string;
	platform: string;
	episodes: EpisodeInfo[];
	sortOrder: "asc" | "desc";
}

function DownloadedIcon({ ep }: { ep: EpisodeInfo }) {
	if (ep.isUserDownloaded) {
		return (
			<Tooltip>
				<TooltipTrigger asChild>
					<CircleCheck className="size-5 text-green-600" />
				</TooltipTrigger>
				<TooltipContent>Downloaded by me</TooltipContent>
			</Tooltip>
		);
	}
	if (ep.isGlobalDownloaded) {
		return (
			<Tooltip>
				<TooltipTrigger asChild>
					<CircleCheck className="size-5 text-blue-600" />
				</TooltipTrigger>
				<TooltipContent>Downloaded by another user</TooltipContent>
			</Tooltip>
		);
	}
	return (
		<Tooltip>
			<TooltipTrigger asChild>
				<CircleX className="size-5 text-destructive" />
			</TooltipTrigger>
			<TooltipContent>Not downloaded</TooltipContent>
		</Tooltip>
	);
}

export function EpisodesTable({
	animeId,
	platform,
	episodes,
	sortOrder,
}: EpisodesTableProps) {
	const queryClient = useQueryClient();
	const parentRef = useRef<HTMLDivElement>(null);
	const [pendingEpisodes, setPendingEpisodes] = useState<Set<number>>(
		new Set(),
	);

	const sortedEpisodes = useMemo(
		() =>
			[...episodes].sort((a, b) =>
				sortOrder === "asc" ? a.id - b.id : b.id - a.id,
			),
		[episodes, sortOrder],
	);

	const downloadMutation = useMutation({
		mutationFn: (episodeNumber: number) => {
			setPendingEpisodes((prev) => new Set(prev).add(episodeNumber));
			return downloadEpisode(animeId, episodeNumber);
		},
		onSuccess: (_, episodeNumber) => {
			setPendingEpisodes((prev) => {
				const next = new Set(prev);
				next.delete(episodeNumber);
				return next;
			});
			toast.success(`Episode ${episodeNumber} queued`);
			queryClient.invalidateQueries({
				queryKey: ["animes", "detail", animeId],
			});
		},
		onError: (error, episodeNumber) => {
			setPendingEpisodes((prev) => {
				const next = new Set(prev);
				next.delete(episodeNumber);
				return next;
			});
			const axiosError = error as AxiosError<{ message: string }>;
			toast.error(axiosError.response?.data?.message ?? "Download failed");
		},
	});

	const virtualizer = useVirtualizer({
		count: sortedEpisodes.length,
		getScrollElement: () => parentRef.current,
		estimateSize: () => 53,
		overscan: 5,
	});

	if (episodes.length === 0) {
		return (
			<div className="p-8 text-center text-sm text-muted-foreground">
				No episodes available.
			</div>
		);
	}

	return (
		<div className="rounded-md border">
			{/* Header — outside the scroll container so it never moves */}
			<div className="grid grid-cols-[80px_1fr_120px_160px] border-b bg-background">
				<div className="p-3 text-xs font-medium text-muted-foreground">#</div>
				<div className="p-3 text-xs font-medium text-muted-foreground">
					Episode
				</div>
				<div className="p-3 text-xs font-medium text-muted-foreground flex justify-center">
					Downloaded
				</div>
				<div className="p-3 text-xs font-medium text-muted-foreground flex justify-center">
					Actions
				</div>
			</div>

			{/* Scrollable virtual rows */}
			<div ref={parentRef} className="h-[60vh] overflow-auto">
				<div
					style={{
						height: `${virtualizer.getTotalSize()}px`,
						position: "relative",
					}}
				>
					{virtualizer.getVirtualItems().map((virtualRow) => {
						const ep = sortedEpisodes[virtualRow.index];
						const episodeUrl = buildEpisodeUrl(platform, animeId, ep.id);

						return (
							<div
								key={virtualRow.key}
								data-index={virtualRow.index}
								ref={virtualizer.measureElement}
								style={{
									position: "absolute",
									top: 0,
									left: 0,
									width: "100%",
									transform: `translateY(${virtualRow.start}px)`,
								}}
								className="grid grid-cols-[80px_1fr_120px_160px] border-b hover:bg-muted/50 items-center"
							>
								<div className="p-3 text-sm">{ep.id}</div>
								<div className="p-3 text-sm">Episode {ep.id}</div>
								<div className="p-3 flex items-center justify-center">
									<DownloadedIcon ep={ep} />
								</div>
								<div className="flex items-center justify-center">
									<Button
										variant="ghost"
										size="icon"
										onClick={() => downloadMutation.mutate(ep.id)}
										disabled={pendingEpisodes.has(ep.id)}
									>
										<Download className="size-4" />
									</Button>

									<a href={episodeUrl || "#"} target="_blank" rel="noreferrer">
										<Button variant="ghost" size="icon">
											<Play className="size-4" />
										</Button>
									</a>
								</div>
							</div>
						);
					})}
				</div>
			</div>
		</div>
	);
}

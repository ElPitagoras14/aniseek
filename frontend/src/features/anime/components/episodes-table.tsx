import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
	useVirtualizer,
	useWindowVirtualizer,
	type Virtualizer,
} from "@tanstack/react-virtual";
import type { AxiosError } from "axios";
import { CircleCheck, CircleX, Download, Play } from "lucide-react";
import { useLayoutEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger,
} from "@/components/ui/tooltip";
import { downloadEpisode } from "@/features/anime/api";
import type { EpisodeInfo } from "@/features/anime/types";
import { useIsMobile } from "@/hooks/use-mobile";

interface EpisodesTableProps {
	animeId: string;
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

// `#` is the episode id sent to the download API; it is kept on mobile because it
// does not always match the list position (e.g. animes with an episode 0).
const ROW_COLS =
	"grid-cols-[3rem_1fr_2.75rem_4.5rem] md:grid-cols-[80px_1fr_120px_160px]";
const ROW_ESTIMATE = 53;

interface EpisodeRowProps {
	ep: EpisodeInfo;
	isPending: boolean;
	onDownload: (episodeNumber: number) => void;
}

function EpisodeRow({ ep, isPending, onDownload }: EpisodeRowProps) {
	return (
		<>
			<div className="p-3 text-sm">{ep.id}</div>
			<div className="min-w-0 truncate p-3 text-sm">Episode {ep.id}</div>
			<div className="flex items-center justify-center p-3">
				<DownloadedIcon ep={ep} />
			</div>
			<div className="flex items-center justify-center">
				<Button
					variant="ghost"
					size="icon"
					onClick={() => onDownload(ep.id)}
					disabled={isPending}
					aria-label={`Download episode ${ep.id}`}
				>
					<Download className="size-4" />
				</Button>

				<a href={ep.url} target="_blank" rel="noreferrer">
					<Button
						variant="ghost"
						size="icon"
						aria-label={`Play episode ${ep.id}`}
					>
						<Play className="size-4" />
					</Button>
				</a>
			</div>
		</>
	);
}

interface EpisodeRowsProps {
	episodes: EpisodeInfo[];
	pendingEpisodes: Set<number>;
	onDownload: (episodeNumber: number) => void;
}

function VirtualRows({
	virtualizer,
	episodes,
	pendingEpisodes,
	onDownload,
	scrollMargin = 0,
}: EpisodeRowsProps & {
	virtualizer:
		| Virtualizer<Window, Element>
		| Virtualizer<HTMLDivElement, Element>;
	scrollMargin?: number;
}) {
	return (
		<div
			style={{
				height: `${virtualizer.getTotalSize()}px`,
				position: "relative",
			}}
		>
			{virtualizer.getVirtualItems().map((virtualRow) => {
				const ep = episodes[virtualRow.index];

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
							transform: `translateY(${virtualRow.start - scrollMargin}px)`,
						}}
						className={`grid ${ROW_COLS} border-b hover:bg-muted/50 items-center`}
					>
						<EpisodeRow
							ep={ep}
							isPending={pendingEpisodes.has(ep.id)}
							onDownload={onDownload}
						/>
					</div>
				);
			})}
		</div>
	);
}

// Desktop: rows scroll inside a fixed-height container.
function EpisodeRowsContained(props: EpisodeRowsProps) {
	const parentRef = useRef<HTMLDivElement>(null);
	const virtualizer = useVirtualizer({
		count: props.episodes.length,
		getScrollElement: () => parentRef.current,
		estimateSize: () => ROW_ESTIMATE,
		overscan: 5,
	});

	return (
		<div ref={parentRef} className="h-[60vh] overflow-y-auto">
			<VirtualRows virtualizer={virtualizer} {...props} />
		</div>
	);
}

// Mobile: rows scroll with the page, so there is no nested scroll trapping the gesture.
function EpisodeRowsWindow(props: EpisodeRowsProps) {
	const listRef = useRef<HTMLDivElement>(null);
	const [scrollMargin, setScrollMargin] = useState(0);

	// The list's page offset changes when content above it resizes (poster load, tabs).
	useLayoutEffect(() => {
		const el = listRef.current;
		if (!el) return;
		const update = () =>
			setScrollMargin(el.getBoundingClientRect().top + window.scrollY);
		update();
		const observer = new ResizeObserver(update);
		observer.observe(document.body);
		return () => observer.disconnect();
	}, []);

	const virtualizer = useWindowVirtualizer({
		count: props.episodes.length,
		estimateSize: () => ROW_ESTIMATE,
		overscan: 5,
		scrollMargin,
	});

	return (
		<div ref={listRef}>
			<VirtualRows
				virtualizer={virtualizer}
				scrollMargin={scrollMargin}
				{...props}
			/>
		</div>
	);
}

export function EpisodesTable({
	animeId,
	episodes,
	sortOrder,
}: EpisodesTableProps) {
	const queryClient = useQueryClient();
	const isMobile = useIsMobile();
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

	if (episodes.length === 0) {
		return (
			<div className="p-8 text-center text-sm text-muted-foreground">
				No episodes available.
			</div>
		);
	}

	const rowsProps: EpisodeRowsProps = {
		episodes: sortedEpisodes,
		pendingEpisodes,
		onDownload: (episodeNumber) => downloadMutation.mutate(episodeNumber),
	};

	return (
		<div className="rounded-md border md:overflow-x-auto">
			<div className="md:min-w-[500px]">
				{/* Header — outside the scrolling rows so it stays put while rows scroll */}
				<div className={`grid ${ROW_COLS} border-b bg-background`}>
					<div className="p-3 text-xs font-medium text-muted-foreground">#</div>
					<div className="p-3 text-xs font-medium text-muted-foreground">
						Episode
					</div>
					<div className="p-3 text-xs font-medium text-muted-foreground flex justify-center">
						<span className="hidden md:inline">Downloaded</span>
						<span className="sr-only md:hidden">Downloaded</span>
					</div>
					<div className="p-3 text-xs font-medium text-muted-foreground flex justify-center">
						<span className="hidden md:inline">Actions</span>
						<span className="sr-only md:hidden">Actions</span>
					</div>
				</div>

				{isMobile ? (
					<EpisodeRowsWindow {...rowsProps} />
				) : (
					<EpisodeRowsContained {...rowsProps} />
				)}
			</div>
		</div>
	);
}

import { useQuery } from "@tanstack/react-query";
import { Clock, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { episodeFileUrl } from "@/features/downloads/api";
import { downloadsLastQueryOptions } from "../api";
import { HomeLastDownloadsSkeleton } from "./home-skeleton";

interface HomeLastDownloadsProps {
	className?: string;
}

function formatRelative(iso: string | null): string {
	if (!iso) return "";
	const date = new Date(iso);
	const now = new Date();
	const diffMs = now.getTime() - date.getTime();
	const diffSec = Math.round(diffMs / 1000);
	const diffMin = Math.round(diffMs / 60_000);
	const diffHr = Math.round(diffMs / 3_600_000);
	const diffDay = Math.round(diffMs / 86_400_000);
	const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
	if (Math.abs(diffSec) < 60) return rtf.format(-diffSec, "second");
	if (Math.abs(diffMin) < 60) return rtf.format(-diffMin, "minute");
	if (Math.abs(diffHr) < 24) return rtf.format(-diffHr, "hour");
	if (Math.abs(diffDay) < 30) return rtf.format(-diffDay, "day");
	return new Intl.DateTimeFormat("en-US", { dateStyle: "medium" }).format(date);
}

export function HomeLastDownloads({ className }: HomeLastDownloadsProps) {
	const { data, isLoading, isError, refetch } = useQuery(
		downloadsLastQueryOptions,
	);

	if (isLoading) {
		return <HomeLastDownloadsSkeleton className={className} />;
	}

	if (isError) {
		return (
			<Card className={className}>
				<CardContent className="flex items-center gap-3">
					<p className="text-sm text-destructive">
						Failed to load recent downloads.
					</p>
					<Button variant="outline" size="sm" onClick={() => refetch()}>
						Retry
					</Button>
				</CardContent>
			</Card>
		);
	}

	const items = data?.items.slice(0, 4) ?? [];

	return (
		<Card className={className}>
			<CardHeader>
				<CardTitle>Recent downloads</CardTitle>
			</CardHeader>
			<CardContent>
				{items.length === 0 ? (
					<div className="flex flex-col gap-2">
						<p className="text-sm text-muted-foreground">No downloads yet.</p>
					</div>
				) : (
					<div className="flex flex-col">
						{items.map((item) => (
							<div
								key={item.id}
								className="flex items-center gap-3 py-2 -mx-4 px-4 first:-mt-2"
							>
								<img
									src={item.poster}
									alt={item.title}
									className="w-10 h-14 object-cover rounded shrink-0"
									loading="lazy"
								/>
								<div className="flex-1 min-w-0">
									<p className="text-sm font-medium truncate">{item.title}</p>
									<p className="text-xs text-muted-foreground">
										Episode {item.episodeNumber} ·{" "}
										{formatRelative(item.downloadedAt)}
									</p>
								</div>
								{item.status === "SUCCESS" ? (
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
								) : (
									<span
										className="text-muted-foreground shrink-0"
										title={item.status}
									>
										<Clock className="size-4" />
									</span>
								)}
							</div>
						))}
					</div>
				)}
			</CardContent>
		</Card>
	);
}

import { HardDrive } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatBytes } from "../lib/format-bytes";
import type { StorageResponse } from "../types";
import { HomeStorageSkeleton } from "./home-skeleton";

interface HomeStorageProps {
	className?: string;
	data: StorageResponse | undefined;
	isLoading: boolean;
	isError: boolean;
	onRetry: () => void;
}

export function HomeStorage({
	className,
	data,
	isLoading,
	isError,
	onRetry,
}: HomeStorageProps) {
	if (isLoading) {
		return <HomeStorageSkeleton className={className} />;
	}

	if (isError) {
		return (
			<Card className={className}>
				<CardContent className="flex items-center gap-3">
					<p className="text-sm text-destructive">
						Failed to load storage info.
					</p>
					<Button variant="outline" size="sm" onClick={onRetry}>
						Retry
					</Button>
				</CardContent>
			</Card>
		);
	}

	const top3 = (data?.items ?? []).slice(0, 3);

	return (
		<Card className={className}>
			<CardHeader>
				<div className="flex items-center justify-between gap-2">
					<div className="flex items-center gap-2">
						<HardDrive className="size-4 text-muted-foreground" />
						<CardTitle>Storage</CardTitle>
					</div>
					<span className="text-2xl font-bold">
						{formatBytes(data?.totalSize ?? 0)}
					</span>
				</div>
			</CardHeader>
			<CardContent>
				{top3.length === 0 ? (
					<p className="text-sm text-muted-foreground">No storage used yet.</p>
				) : (
					<ul className="flex flex-col gap-2">
						{top3.map((item) => (
							<li
								key={item.id}
								className="flex items-center justify-between gap-2"
							>
								<span className="text-sm truncate flex-1">{item.title}</span>
								<span className="text-xs text-muted-foreground shrink-0">
									{formatBytes(item.size)}
								</span>
							</li>
						))}
					</ul>
				)}
			</CardContent>
		</Card>
	);
}

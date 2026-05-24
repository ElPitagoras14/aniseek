import { Skeleton } from "@/components/ui/skeleton";
import { ROW_COLS } from "./download-row";

export function DownloadRowSkeleton() {
	return (
		<div className={`grid ${ROW_COLS} items-center gap-4 px-4 py-2 border-b`}>
			<Skeleton className="aspect-2/3 w-full rounded" />

			<Skeleton className="h-4 w-3/4" />

			<Skeleton className="h-3 w-10 mx-auto" />

			<Skeleton className="h-2.5 w-full rounded-full" />

			<Skeleton className="h-3 w-14 mx-auto" />

			<Skeleton className="size-8 rounded-md mx-auto" />
		</div>
	);
}

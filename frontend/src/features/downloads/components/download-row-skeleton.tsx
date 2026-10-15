import { Skeleton } from "@/components/ui/skeleton";
import { ROW_COLS } from "./download-row";

export function DownloadRowSkeleton() {
	return (
		<div
			className={`flex items-start gap-3 border-b px-3 py-3 md:grid ${ROW_COLS} md:items-center md:gap-4 md:px-4 md:py-2`}
		>
			<Skeleton className="aspect-2/3 w-12 shrink-0 rounded md:w-full" />

			<div className="flex min-w-0 flex-1 flex-col gap-2 md:contents">
				<Skeleton className="h-4 w-3/4" />

				<Skeleton className="h-3 w-24 md:hidden" />

				<Skeleton className="mx-auto hidden h-3 w-10 md:block" />

				<Skeleton className="h-2.5 w-full rounded-full" />

				<Skeleton className="mx-auto hidden h-3 w-14 md:block" />
			</div>

			<Skeleton className="mx-auto size-8 shrink-0 rounded-md" />
		</div>
	);
}

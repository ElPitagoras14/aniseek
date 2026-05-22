import { Skeleton } from "@/components/ui/skeleton";

export function DownloadRowSkeleton() {
	return (
		<div className="flex items-start gap-4 p-3 border-b">
			<Skeleton className="w-16 md:w-20 aspect-[2/3] rounded-md flex-shrink-0" />
			<div className="flex flex-col gap-2 flex-1 min-w-0">
				<Skeleton className="h-4 w-3/4" />
				<Skeleton className="h-3 w-1/2" />
				<Skeleton className="h-1.5 w-full" />
			</div>
			<div className="flex gap-2 ml-auto flex-shrink-0">
				<Skeleton className="h-9 w-9 rounded-md" />
				<Skeleton className="h-9 w-9 rounded-md" />
			</div>
		</div>
	);
}

import { Skeleton } from "@/components/ui/skeleton";

export function AnimeDetailSkeleton() {
	return (
		<div className="grid grid-cols-1 md:grid-cols-4 gap-6">
			{/* Left column: poster skeleton */}
			<div className="flex flex-col gap-4">
				<Skeleton className="aspect-2/3 w-full rounded-md" />
				<Skeleton className="h-6 w-24" />
				<div className="flex flex-wrap gap-2">
					<Skeleton className="h-5 w-16" />
					<Skeleton className="h-5 w-20" />
					<Skeleton className="h-5 w-14" />
				</div>
			</div>
			{/* Right column: content skeleton */}
			<div className="md:col-span-3 flex flex-col gap-4">
				<div className="flex justify-between items-start">
					<div className="flex flex-col gap-2">
						<Skeleton className="h-8 w-64" />
						<Skeleton className="h-4 w-48" />
					</div>
					<Skeleton className="h-9 w-36" />
				</div>
				<div className="flex gap-2">
					<Skeleton className="h-10 w-28" />
					<Skeleton className="h-10 w-28" />
				</div>
				<Skeleton className="h-4 w-full" />
				<Skeleton className="h-4 w-full" />
				<Skeleton className="h-4 w-3/4" />
			</div>
		</div>
	);
}

import { Skeleton } from "@/components/ui/skeleton";

export function CalendarByDaySkeleton() {
	return (
		<div className="flex flex-col gap-4">
			<Skeleton className="h-9 w-full max-w-md" />
			<div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
				{Array.from({ length: 6 }).map((_, i) => (
					<div
						// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton
						key={i}
						className="flex flex-col gap-1.5"
					>
						<Skeleton className="aspect-[2/3] w-full max-w-[90px] rounded-md" />
						<Skeleton className="h-3 w-3/4 max-w-[90px]" />
					</div>
				))}
			</div>
		</div>
	);
}

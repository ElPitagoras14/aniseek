import { Skeleton } from "@/components/ui/skeleton";
import { WEEK_DAYS } from "../lib/week-days";

export function CalendarGridSkeleton() {
	return (
		<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4">
			{WEEK_DAYS.map((day) => (
				<div
					key={day}
					className="flex flex-col gap-3 rounded-lg border p-3 min-h-[200px]"
				>
					<Skeleton className="h-5 w-20 mx-auto" />
					{Array.from({ length: 3 }).map((_, i) => (
						<div
							// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton
							key={i}
							className="flex flex-col gap-1.5"
						>
							<Skeleton className="aspect-[2/3] w-full rounded-md" />
							<Skeleton className="h-3 w-3/4" />
						</div>
					))}
				</div>
			))}
		</div>
	);
}

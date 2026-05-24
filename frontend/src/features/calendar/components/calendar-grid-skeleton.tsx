import { Skeleton } from "@/components/ui/skeleton";
import { WEEK_DAYS } from "../lib/week-days";

export function CalendarGridSkeleton() {
	return (
		<div className="border rounded-lg overflow-hidden">
			<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7">
				{WEEK_DAYS.map((day) => (
					<div
						key={day}
						className="flex flex-col gap-2 p-3 min-h-[160px] border-r last:border-r-0"
					>
						<Skeleton className="h-5 w-20 mx-auto" />
						{Array.from({ length: 3 }).map((_, i) => (
							<Skeleton
								// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton
								key={i}
								className="h-10 w-full rounded-md"
							/>
						))}
					</div>
				))}
			</div>
		</div>
	);
}

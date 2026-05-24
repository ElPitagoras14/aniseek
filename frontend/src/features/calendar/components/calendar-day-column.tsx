import { cn } from "@/lib/utils";
import type { InEmissionAnime, WeekDay } from "../types";
import { CalendarTableCard } from "./calendar-table-card";

interface CalendarDayColumnProps {
	day: WeekDay;
	animes: InEmissionAnime[];
	isToday: boolean;
}

export function CalendarDayColumn({
	day,
	animes,
	isToday,
}: CalendarDayColumnProps) {
	return (
		<div
			className={cn(
				"flex flex-col gap-2 rounded-lg border p-3 min-h-[160px]",
				isToday && "border-primary/60 bg-primary/5",
			)}
		>
			<div
				className={cn(
					"text-sm font-semibold text-center pb-2 border-b",
					isToday && "text-primary",
				)}
			>
				{day}
			</div>
			<div className="flex flex-col gap-2">
				{animes.map((anime) => (
					<CalendarTableCard key={anime.id} anime={anime} />
				))}
			</div>
		</div>
	);
}

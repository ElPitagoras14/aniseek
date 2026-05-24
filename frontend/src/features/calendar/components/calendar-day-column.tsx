import { cn } from "@/lib/utils";
import type { InEmissionAnime, WeekDay } from "../types";
import { CalendarAnimeCard } from "./calendar-anime-card";

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
				"flex flex-col gap-3 rounded-lg border p-3 min-h-[200px]",
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
			<div className="flex flex-col gap-3">
				{animes.map((anime) => (
					<CalendarAnimeCard key={anime.id} anime={anime} />
				))}
			</div>
		</div>
	);
}

import { useMemo } from "react";
import {
	getTodayWeekDay,
	groupAnimesByWeekDay,
	WEEK_DAYS,
} from "../lib/week-days";
import type { InEmissionAnime } from "../types";
import { CalendarDayColumn } from "./calendar-day-column";
import { CalendarGridSkeleton } from "./calendar-grid-skeleton";

interface CalendarGridProps {
	animes: InEmissionAnime[] | undefined;
	isLoading: boolean;
	isError: boolean;
	error: Error | null;
}

export function CalendarGrid({
	animes,
	isLoading,
	isError,
	error,
}: CalendarGridProps) {
	const grouped = useMemo(
		() => (animes ? groupAnimesByWeekDay(animes) : null),
		[animes],
	);
	const today = getTodayWeekDay();

	if (isLoading) return <CalendarGridSkeleton />;

	if (isError) {
		return (
			<p className="text-destructive text-sm">
				{error?.message ?? "Failed to load schedule"}
			</p>
		);
	}

	if (!grouped) {
		return (
			<p className="text-muted-foreground text-sm">No schedule available.</p>
		);
	}

	return (
		<div className="border rounded-lg overflow-hidden">
			<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7">
				{WEEK_DAYS.map((day) => (
					<CalendarDayColumn
						key={day}
						day={day}
						animes={grouped[day]}
						isToday={day === today}
					/>
				))}
			</div>
		</div>
	);
}

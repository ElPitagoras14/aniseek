import { useMemo } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import {
	getTodayWeekDay,
	groupAnimesByWeekDay,
	WEEK_DAYS,
} from "../lib/week-days";
import type { InEmissionAnime } from "../types";
import { CalendarAnimeCard } from "./calendar-anime-card";
import { CalendarByDaySkeleton } from "./calendar-by-day-skeleton";

interface CalendarByDayProps {
	animes: InEmissionAnime[] | undefined;
	isLoading: boolean;
	isError: boolean;
	error: Error | null;
}

export function CalendarByDay({
	animes,
	isLoading,
	isError,
	error,
}: CalendarByDayProps) {
	const grouped = useMemo(
		() => (animes ? groupAnimesByWeekDay(animes) : null),
		[animes],
	);
	const today = getTodayWeekDay();

	if (isLoading) return <CalendarByDaySkeleton />;

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
		<Tabs defaultValue={today} className="flex flex-col gap-4">
			<div className="overflow-x-auto">
				<TabsList className="w-full min-w-max">
					{WEEK_DAYS.map((day) => {
						const count = grouped[day].length;
						return (
							<TabsTrigger
								key={day}
								value={day}
								className={cn(day === today && "text-primary", "min-w-24")}
							>
								<span className="hidden sm:inline">{day}</span>
								<span className="sm:hidden">{day.slice(0, 3)}</span>
								{count > 0 && <span className="opacity-60">({count})</span>}
							</TabsTrigger>
						);
					})}
				</TabsList>
			</div>
			{WEEK_DAYS.map((day) => (
				<TabsContent key={day} value={day}>
					{grouped[day].length === 0 ? (
						<p className="text-muted-foreground text-sm py-4">
							No animes airing on {day}.
						</p>
					) : (
						<div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
							{grouped[day].map((anime) => (
								<CalendarAnimeCard key={anime.id} anime={anime} />
							))}
						</div>
					)}
				</TabsContent>
			))}
		</Tabs>
	);
}

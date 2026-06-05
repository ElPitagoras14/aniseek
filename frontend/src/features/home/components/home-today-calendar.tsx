import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { Calendar } from "lucide-react";
import { useMemo } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { inEmissionQueryOptions } from "@/features/calendar/api";
import { CalendarAnimeCard } from "@/features/calendar/components/calendar-anime-card";
import { todayWeekday } from "../lib/today-weekday";
import { HomeTodayCalendarSkeleton } from "./home-skeleton";

interface HomeTodayCalendarProps {
	className?: string;
}

export function HomeTodayCalendar({ className }: HomeTodayCalendarProps) {
	const { data, isLoading, isError, refetch } = useQuery(
		inEmissionQueryOptions,
	);
	const today = todayWeekday();

	const todaysAnimes = useMemo(
		() => (data ?? []).filter((a) => a.weekDay === today).slice(0, 4),
		[data, today],
	);

	if (isLoading) {
		return <HomeTodayCalendarSkeleton className={className} />;
	}

	if (isError) {
		return (
			<Card className={className}>
				<CardContent className="flex items-center gap-3">
					<p className="text-sm text-destructive">
						Failed to load today's schedule.
					</p>
					<Button variant="outline" size="sm" onClick={() => refetch()}>
						Retry
					</Button>
				</CardContent>
			</Card>
		);
	}

	return (
		<Card className={className}>
			<CardHeader>
				<div className="flex items-center gap-2">
					<Calendar className="size-4 text-muted-foreground" />
					<CardTitle>Today</CardTitle>
					<Badge variant="outline">{today}</Badge>
				</div>
			</CardHeader>
			<CardContent>
				{todaysAnimes.length === 0 ? (
					<div className="flex flex-col gap-2">
						<p className="text-sm text-muted-foreground">
							No animes airing today.
						</p>
						<Link
							to="/calendar"
							className="text-sm text-primary hover:underline w-fit"
						>
							Browse calendar
						</Link>
					</div>
				) : (
					<div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
						{todaysAnimes.map((anime) => (
							<CalendarAnimeCard key={anime.id} anime={anime} />
						))}
					</div>
				)}
			</CardContent>
		</Card>
	);
}

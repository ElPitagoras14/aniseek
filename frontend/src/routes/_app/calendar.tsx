import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { inEmissionQueryOptions } from "@/features/calendar/api";
import { CalendarByDay } from "@/features/calendar/components/calendar-by-day";
import { CalendarGrid } from "@/features/calendar/components/calendar-grid";
import { CalendarHeader } from "@/features/calendar/components/calendar-header";
import {
	type CalendarViewMode,
	CalendarViewToggle,
} from "@/features/calendar/components/calendar-view-toggle";
import { useIsMobile } from "@/hooks/use-mobile";

export const Route = createFileRoute("/_app/calendar")({
	component: CalendarPage,
});

function CalendarPage() {
	const isMobile = useIsMobile();
	const [viewMode, setViewMode] = useState<CalendarViewMode>("table");
	const effectiveMode: CalendarViewMode = isMobile ? "day" : viewMode;

	const { data, isLoading, isError, error } = useQuery(inEmissionQueryOptions);

	return (
		<div className="p-4 md:p-6 flex flex-col gap-6">
			<div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
				<CalendarHeader />
				{!isMobile && (
					<CalendarViewToggle value={viewMode} onChange={setViewMode} />
				)}
			</div>
			{effectiveMode === "table" ? (
				<CalendarGrid
					animes={data}
					isLoading={isLoading}
					isError={isError}
					error={error}
				/>
			) : (
				<CalendarByDay
					animes={data}
					isLoading={isLoading}
					isError={isError}
					error={error}
				/>
			)}
		</div>
	);
}

import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { inEmissionQueryOptions } from "@/features/calendar/api";
import { CalendarGrid } from "@/features/calendar/components/calendar-grid";
import { CalendarHeader } from "@/features/calendar/components/calendar-header";

export const Route = createFileRoute("/_app/calendar")({
	component: CalendarPage,
});

function CalendarPage() {
	const { data, isLoading, isError, error } = useQuery(inEmissionQueryOptions);

	return (
		<div className="p-4 md:p-6 flex flex-col gap-6">
			<CalendarHeader />
			<CalendarGrid
				animes={data}
				isLoading={isLoading}
				isError={isError}
				error={error}
			/>
		</div>
	);
}

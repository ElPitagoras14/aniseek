import type { WeekDay } from "@/features/calendar/types";

export function todayWeekday(): WeekDay {
	const day = new Intl.DateTimeFormat("en-US", { weekday: "long" }).format(
		new Date(),
	);
	return day as WeekDay;
}

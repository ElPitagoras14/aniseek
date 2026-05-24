import type { InEmissionAnime, WeekDay } from "../types";

export const WEEK_DAYS: readonly WeekDay[] = [
	"Monday",
	"Tuesday",
	"Wednesday",
	"Thursday",
	"Friday",
	"Saturday",
	"Sunday",
] as const;

// JS Date#getDay() returns 0=Sun..6=Sat. Map to our Monday-first order.
const JS_DAY_TO_WEEKDAY: WeekDay[] = [
	"Sunday",
	"Monday",
	"Tuesday",
	"Wednesday",
	"Thursday",
	"Friday",
	"Saturday",
];

export function getTodayWeekDay(now: Date = new Date()): WeekDay {
	return JS_DAY_TO_WEEKDAY[now.getDay()];
}

export function groupAnimesByWeekDay(
	items: InEmissionAnime[],
): Record<WeekDay, InEmissionAnime[]> {
	const acc: Record<WeekDay, InEmissionAnime[]> = {
		Monday: [],
		Tuesday: [],
		Wednesday: [],
		Thursday: [],
		Friday: [],
		Saturday: [],
		Sunday: [],
	};
	for (const item of items) {
		acc[item.weekDay]?.push(item);
	}
	return acc;
}

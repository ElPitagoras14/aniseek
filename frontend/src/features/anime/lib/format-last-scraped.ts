export function formatLastScraped(iso: string | null): string {
	if (!iso) return "Nunca actualizado";

	const date = new Date(iso);
	const now = new Date();
	const diffMs = now.getTime() - date.getTime();
	const diffDays = diffMs / (1000 * 60 * 60 * 24);

	if (diffDays < 7) {
		const rtf = new Intl.RelativeTimeFormat("es", { numeric: "auto" });
		const diffSeconds = Math.round(diffMs / 1000);
		const diffMinutes = Math.round(diffMs / (1000 * 60));
		const diffHours = Math.round(diffMs / (1000 * 60 * 60));
		const diffDaysRounded = Math.round(diffDays);

		if (diffSeconds < 60) return rtf.format(-diffSeconds, "second");
		if (diffMinutes < 60) return rtf.format(-diffMinutes, "minute");
		if (diffHours < 24) return rtf.format(-diffHours, "hour");
		return rtf.format(-diffDaysRounded, "day");
	}

	return new Intl.DateTimeFormat("es", {
		dateStyle: "medium",
		timeStyle: "short",
	}).format(date);
}

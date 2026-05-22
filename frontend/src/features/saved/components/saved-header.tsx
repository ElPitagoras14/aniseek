interface SavedHeaderProps {
	count: number | undefined;
	isLoading: boolean;
}

export function SavedHeader({ count, isLoading }: SavedHeaderProps) {
	const subtitle = (() => {
		if (isLoading) return "Loading your saved animes...";
		if (count === undefined) return "Animes you have saved";
		if (count === 0) return "You haven't saved any anime yet";
		return `${count} anime${count !== 1 ? "s" : ""} saved`;
	})();

	return (
		<div className="flex flex-col gap-1">
			<h1 className="text-2xl font-semibold">Saved animes</h1>
			<p className="text-sm text-muted-foreground">{subtitle}</p>
		</div>
	);
}

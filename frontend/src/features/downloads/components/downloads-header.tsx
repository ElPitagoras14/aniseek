import { DownloadsSearchInput } from "./downloads-search-input";

interface DownloadsHeaderProps {
	defaultValue?: string;
	onSearch: (value: string) => void;
}

export function DownloadsHeader({
	defaultValue = "",
	onSearch,
}: DownloadsHeaderProps) {
	return (
		<div className="flex flex-col gap-1">
			<h1 className="text-2xl font-semibold">Descargas</h1>
			<DownloadsSearchInput
				defaultValue={defaultValue}
				onDebouncedChange={onSearch}
			/>
		</div>
	);
}

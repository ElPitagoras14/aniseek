import { ArrowUpDown, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuCheckboxItem,
	DropdownMenuContent,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import type { SortOption, StatusFilter } from "../types";

interface SavedFiltersProps {
	search: string;
	onSearchChange: (value: string) => void;
	sort: SortOption;
	onSortChange: (sort: SortOption) => void;
	status: StatusFilter;
	onStatusChange: (status: StatusFilter) => void;
}

const SORT_LABEL: Record<string, string> = {
	"title-asc": "Title (A-Z)",
	"title-desc": "Title (Z-A)",
	"saveDate-desc": "Recently saved",
	"saveDate-asc": "Oldest saved",
};

export function SavedFilters({
	search,
	onSearchChange,
	sort,
	onSortChange,
	status,
	onStatusChange,
}: SavedFiltersProps) {
	const sortKey = `${sort.field}-${sort.order}`;

	return (
		<div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
			<div className="relative flex-1 max-w-xl">
				<Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
				<Input
					value={search}
					onChange={(e) => onSearchChange(e.target.value)}
					placeholder="Filter saved animes..."
					className="pl-9"
				/>
			</div>
			<div className="flex gap-2">
				<Select
					value={status}
					onValueChange={(v) => onStatusChange(v as StatusFilter)}
				>
					<SelectTrigger className="w-[160px]">
						<SelectValue />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">All animes</SelectItem>
						<SelectItem value="airing">Airing</SelectItem>
						<SelectItem value="finished">Finished</SelectItem>
					</SelectContent>
				</Select>
				<DropdownMenu>
					<DropdownMenuTrigger asChild>
						<Button variant="outline" className="gap-2">
							<ArrowUpDown className="size-4" />
							<span className="hidden sm:inline">{SORT_LABEL[sortKey]}</span>
						</Button>
					</DropdownMenuTrigger>
					<DropdownMenuContent align="end">
						<DropdownMenuLabel>Sort by</DropdownMenuLabel>
						<DropdownMenuSeparator />
						<DropdownMenuCheckboxItem
							checked={sortKey === "saveDate-desc"}
							onCheckedChange={() =>
								onSortChange({ field: "saveDate", order: "desc" })
							}
						>
							Recently saved
						</DropdownMenuCheckboxItem>
						<DropdownMenuCheckboxItem
							checked={sortKey === "saveDate-asc"}
							onCheckedChange={() =>
								onSortChange({ field: "saveDate", order: "asc" })
							}
						>
							Oldest saved
						</DropdownMenuCheckboxItem>
						<DropdownMenuCheckboxItem
							checked={sortKey === "title-asc"}
							onCheckedChange={() =>
								onSortChange({ field: "title", order: "asc" })
							}
						>
							Title (A-Z)
						</DropdownMenuCheckboxItem>
						<DropdownMenuCheckboxItem
							checked={sortKey === "title-desc"}
							onCheckedChange={() =>
								onSortChange({ field: "title", order: "desc" })
							}
						>
							Title (Z-A)
						</DropdownMenuCheckboxItem>
					</DropdownMenuContent>
				</DropdownMenu>
			</div>
		</div>
	);
}

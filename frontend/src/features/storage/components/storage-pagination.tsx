import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";

const LIMIT_OPTIONS = [5, 10, 20, 50] as const;

interface StoragePaginationProps {
	page: number;
	total: number;
	limit: number;
	onPageChange: (page: number) => void;
	onLimitChange: (limit: number) => void;
}

export function StoragePagination({
	page,
	total,
	limit,
	onPageChange,
	onLimitChange,
}: StoragePaginationProps) {
	const totalPages = Math.max(1, Math.ceil(total / limit));

	return (
		<div className="flex items-center justify-end gap-2 pt-4">
			<span className="text-sm text-muted-foreground">Rows per page</span>
			<Select
				value={String(limit)}
				onValueChange={(v) => onLimitChange(Number(v))}
			>
				<SelectTrigger className="h-7 w-16 text-sm">
					<SelectValue />
				</SelectTrigger>
				<SelectContent>
					{LIMIT_OPTIONS.map((o) => (
						<SelectItem key={o} value={String(o)}>
							{o}
						</SelectItem>
					))}
				</SelectContent>
			</Select>
			<span className="text-sm text-muted-foreground">
				Page {page} of {totalPages}
			</span>
			<Button
				variant="outline"
				size="icon"
				className="size-7"
				onClick={() => onPageChange(page - 1)}
				disabled={page <= 1}
			>
				<ChevronLeft className="size-4" />
			</Button>
			<Button
				variant="outline"
				size="icon"
				className="size-7"
				onClick={() => onPageChange(page + 1)}
				disabled={page >= totalPages}
			>
				<ChevronRight className="size-4" />
			</Button>
		</div>
	);
}

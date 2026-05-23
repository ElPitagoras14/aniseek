import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DownloadsPaginationProps {
	page: number;
	total: number;
	limit: number;
	onPageChange: (page: number) => void;
}

export function DownloadsPagination({
	page,
	total,
	limit,
	onPageChange,
}: DownloadsPaginationProps) {
	const totalPages = Math.max(1, Math.ceil(total / limit));

	return (
		<div className="flex items-center justify-end gap-2 pt-4">
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

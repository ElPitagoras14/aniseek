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

	if (totalPages <= 1) return null;

	return (
		<div className="flex items-center justify-between pt-4">
			<Button
				variant="outline"
				size="sm"
				onClick={() => onPageChange(page - 1)}
				disabled={page <= 1}
			>
				<ChevronLeft className="size-4 mr-1" />
				Anterior
			</Button>
			<span className="text-sm text-muted-foreground">
				Página {page} de {totalPages}
			</span>
			<Button
				variant="outline"
				size="sm"
				onClick={() => onPageChange(page + 1)}
				disabled={page >= totalPages}
			>
				Siguiente
				<ChevronRight className="size-4 ml-1" />
			</Button>
		</div>
	);
}

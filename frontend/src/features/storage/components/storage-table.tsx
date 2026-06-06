import {
	Table,
	TableHeader,
	TableBody,
	TableHead,
	TableRow,
	TableCell,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { StoragePagination } from "./storage-pagination";
import { DeleteAnimeDialog } from "./delete-anime-dialog";
import { formatBytes } from "@/lib/format-bytes";
import type { StorageResponse } from "@/features/storage/types";

interface StorageTableProps {
	data: StorageResponse | undefined;
	isLoading: boolean;
	isError: boolean;
	refetch: () => void;
	page: number;
	limit: number;
	onPageChange: (page: number) => void;
	onLimitChange: (limit: number) => void;
}

export function StorageTable({
	data,
	isLoading,
	isError,
	refetch,
	page,
	limit,
	onPageChange,
	onLimitChange,
}: StorageTableProps) {
	return (
		<div>
			<Table>
				<TableHeader>
					<TableRow>
						<TableHead className="w-12">#</TableHead>
						<TableHead>Anime</TableHead>
						<TableHead className="text-right">Size</TableHead>
						<TableHead className="w-12" />
					</TableRow>
				</TableHeader>
				<TableBody>
					{isLoading ? (
						Array.from({ length: 5 }).map((_, i) => (
							<TableRow key={i}>
								<TableCell>
									<Skeleton className="h-4 w-6" />
								</TableCell>
								<TableCell>
									<Skeleton className="h-4 w-48" />
								</TableCell>
								<TableCell className="text-right">
									<Skeleton className="h-4 w-16 ml-auto" />
								</TableCell>
								<TableCell />
							</TableRow>
						))
					) : isError ? (
						<TableRow>
							<TableCell colSpan={3}>
								<div className="flex items-center gap-3 py-4">
									<p className="text-sm text-destructive">
										Failed to load storage data.
									</p>
									<Button variant="outline" size="sm" onClick={refetch}>
										Retry
									</Button>
								</div>
							</TableCell>
						</TableRow>
					) : (data?.items ?? []).length === 0 ? (
						<TableRow>
							<TableCell
								colSpan={3}
								className="text-center text-sm text-muted-foreground py-8"
							>
								No storage data.
							</TableCell>
						</TableRow>
					) : (
						(data?.items ?? []).map((item, index) => (
							<TableRow key={item.id}>
								<TableCell className="text-muted-foreground">
									{(page - 1) * limit + index + 1}
								</TableCell>
								<TableCell className="max-w-xs truncate">{item.title}</TableCell>
								<TableCell className="text-right">
									{formatBytes(item.size)}
								</TableCell>
								<TableCell>
									<DeleteAnimeDialog anime={item} />
								</TableCell>
							</TableRow>
						))
					)}
				</TableBody>
			</Table>
			{!isLoading && !isError && (
				<StoragePagination
					page={page}
					total={data?.total ?? 0}
					limit={limit}
					onPageChange={onPageChange}
					onLimitChange={onLimitChange}
				/>
			)}
		</div>
	);
}

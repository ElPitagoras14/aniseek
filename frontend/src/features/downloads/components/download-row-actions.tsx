import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { Download, Eye, MoreVertical, RefreshCw, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
	deleteEpisodeDownload,
	episodeFileUrl,
	retryEpisodeDownload,
} from "../api";
import type { DownloadStatus } from "../types";

interface DownloadRowActionsProps {
	id: number;
	animeId: string;
	episodeNumber: number;
	status: DownloadStatus;
}

export function DownloadRowActions({
	id,
	animeId,
	episodeNumber,
	status,
}: DownloadRowActionsProps) {
	const queryClient = useQueryClient();

	const deleteMutation = useMutation({
		mutationFn: () => deleteEpisodeDownload(animeId, episodeNumber),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["episodes", "downloads"] });
			toast.success("Descarga eliminada");
		},
		onError: () => toast.error("Error al eliminar la descarga"),
	});

	const retryMutation = useMutation({
		mutationFn: () => retryEpisodeDownload(animeId, episodeNumber),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["episodes", "downloads"] });
			toast.success("Descarga reiniciada");
		},
		onError: () => toast.error("Error al reintentar la descarga"),
	});

	const isActive =
		status === "DOWNLOADING" ||
		status === "GETTING-LINK" ||
		status === "PENDING" ||
		status === "RETRYING";
	const canDownload = status === "SUCCESS";

	return (
		<div className="flex items-center gap-2 flex-shrink-0">
			{canDownload ? (
				<Button
					variant="outline"
					size="icon"
					asChild
					aria-label="Descargar episodio"
				>
					<a href={episodeFileUrl(id)} download>
						<Download className="size-4" />
					</a>
				</Button>
			) : (
				<Button
					variant="outline"
					size="icon"
					disabled
					aria-label="Descargar episodio"
				>
					<Download className="size-4" />
				</Button>
			)}

			<DropdownMenu>
				<DropdownMenuTrigger asChild>
					<Button variant="ghost" size="icon" aria-label="Más opciones">
						<MoreVertical className="size-4" />
					</Button>
				</DropdownMenuTrigger>
				<DropdownMenuContent align="end">
					<DropdownMenuItem
						onClick={() => retryMutation.mutate()}
						disabled={isActive || retryMutation.isPending}
					>
						<RefreshCw className="size-4 mr-2" />
						Reintentar
					</DropdownMenuItem>
					<DropdownMenuItem
						onClick={() => deleteMutation.mutate()}
						disabled={isActive || deleteMutation.isPending}
						className="text-destructive focus:text-destructive"
					>
						<Trash2 className="size-4 mr-2" />
						Eliminar
					</DropdownMenuItem>
					<DropdownMenuItem asChild>
						<Link to="/anime/$slug" params={{ slug: animeId }}>
							<Eye className="size-4 mr-2" />
							Ver anime
						</Link>
					</DropdownMenuItem>
				</DropdownMenuContent>
			</DropdownMenu>
		</div>
	);
}

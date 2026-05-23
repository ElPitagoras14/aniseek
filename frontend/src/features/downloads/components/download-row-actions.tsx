import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { Eye, MoreVertical, RefreshCw, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { deleteEpisodeDownload, retryEpisodeDownload } from "../api";
import type { DownloadStatus } from "../types";

interface DownloadRowActionsProps {
	animeId: string;
	episodeNumber: number;
	status: DownloadStatus;
}

export function DownloadRowActions({
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

	return (
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
	);
}

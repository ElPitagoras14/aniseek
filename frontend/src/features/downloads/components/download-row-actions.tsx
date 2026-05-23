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
			toast.success("Download deleted");
		},
		onError: () => toast.error("Failed to delete download"),
	});

	const retryMutation = useMutation({
		mutationFn: () => retryEpisodeDownload(animeId, episodeNumber),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["episodes", "downloads"] });
			toast.success("Download retried");
		},
		onError: () => toast.error("Failed to retry download"),
	});

	const isActive =
		status === "DOWNLOADING" ||
		status === "GETTING-LINK" ||
		status === "PENDING" ||
		status === "RETRYING";

	return (
		<DropdownMenu>
			<DropdownMenuTrigger asChild>
				<Button variant="ghost" size="icon" aria-label="More options">
					<MoreVertical className="size-4" />
				</Button>
			</DropdownMenuTrigger>
			<DropdownMenuContent align="end">
				<DropdownMenuItem
					onClick={() => retryMutation.mutate()}
					disabled={retryMutation.isPending}
				>
					<RefreshCw className="size-4 mr-2" />
					Retry
				</DropdownMenuItem>
				<DropdownMenuItem
					onClick={() => deleteMutation.mutate()}
					disabled={isActive || deleteMutation.isPending}
					className="text-destructive focus:text-destructive"
				>
					<Trash2 className="size-4 mr-2" />
					Delete
				</DropdownMenuItem>
				<DropdownMenuItem asChild>
					<Link to="/anime/$slug" params={{ slug: animeId }}>
						<Eye className="size-4 mr-2" />
						View anime
					</Link>
				</DropdownMenuItem>
			</DropdownMenuContent>
		</DropdownMenu>
	);
}

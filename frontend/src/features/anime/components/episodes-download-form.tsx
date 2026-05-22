import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { ArrowDown, ArrowUp, Download, Loader2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { downloadEpisodesBulk } from "@/features/anime/api";
import { parseEpisodeRange } from "@/features/anime/lib/parse-episode-range";

interface EpisodesDownloadFormProps {
	animeId: string;
	maxEpisode: number;
	sortOrder: "asc" | "desc";
	onToggleSort: () => void;
}

export function EpisodesDownloadForm({
	animeId,
	maxEpisode,
	sortOrder,
	onToggleSort,
}: EpisodesDownloadFormProps) {
	const [inputValue, setInputValue] = useState("");
	const queryClient = useQueryClient();

	const mutation = useMutation({
		mutationFn: (eps: number[]) => downloadEpisodesBulk(animeId, eps),
		onSuccess: (result) => {
			const successCount = result.data.payload.items.filter(
				(i) => i.success,
			).length;
			toast.success(
				`${successCount}/${result.data.payload.total} episodes queued`,
			);
			setInputValue("");
			queryClient.invalidateQueries({
				queryKey: ["animes", "detail", animeId],
			});
		},
		onError: (error) => {
			const axiosError = error as AxiosError<{ message: string }>;
			toast.error(axiosError.response?.data?.message ?? "Download failed");
		},
	});

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		const { episodes, error } = parseEpisodeRange(inputValue, maxEpisode);
		if (error) {
			toast.error(error);
			return;
		}
		if (episodes.length === 0) {
			toast.error("Enter at least one episode.");
			return;
		}
		mutation.mutate(episodes);
	};

	return (
		<form onSubmit={handleSubmit} className="flex gap-2 items-center">
			<Input
				value={inputValue}
				onChange={(e) => setInputValue(e.target.value)}
				placeholder="e.g. 1-3, 5, 7-9"
				className="flex-1 h-9"
			/>
			<Button
				type="button"
				variant="outline"
				size="icon-lg"
				onClick={onToggleSort}
				title={sortOrder === "asc" ? "Sort descending" : "Sort ascending"}
			>
				{sortOrder === "asc" ? (
					<ArrowUp className="size-4" />
				) : (
					<ArrowDown className="size-4" />
				)}
			</Button>
			<Button type="submit" size="lg" disabled={mutation.isPending}>
				{mutation.isPending ? (
					<Loader2 className="size-4 animate-spin" />
				) : (
					<Download className="size-4" />
				)}
				Download
			</Button>
		</form>
	);
}

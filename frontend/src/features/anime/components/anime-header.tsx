import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { refreshAnime } from "@/features/anime/api";
import { formatLastScraped } from "@/features/anime/lib/format-last-scraped";
import type { AnimeDetail } from "@/features/anime/types";

interface AnimeHeaderProps {
	anime: AnimeDetail;
}

export function AnimeHeader({ anime }: AnimeHeaderProps) {
	const queryClient = useQueryClient();

	const mutation = useMutation({
		mutationFn: () => refreshAnime(anime.id),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: ["animes", "detail", anime.id],
			});
			toast.success("Anime info updated");
		},
		onError: (error) => {
			const axiosError = error as AxiosError<{ message: string }>;
			const message =
				axiosError.response?.data?.message ?? axiosError.message ?? "Error";
			toast.error(message);
		},
	});

	return (
		<div className="flex justify-between gap-4 items-center">
			<div>
				<h1 className="text-2xl font-semibold">{anime.title}</h1>
				<p className="text-sm text-muted-foreground">
					Last updated: {formatLastScraped(anime.lastScrapedAt)}
				</p>
			</div>
			<Button
				disabled={mutation.isPending}
				size="lg"
				onClick={() => mutation.mutate()}
				className="bg-destructive/60 px-6 py-5"
			>
				{mutation.isPending ? "Refreshing…" : "Update Info"}
			</Button>
		</div>
	);
}

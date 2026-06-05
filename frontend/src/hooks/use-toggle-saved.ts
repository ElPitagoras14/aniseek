import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { useState } from "react";
import { toast } from "sonner";
import { saveAnime, unsaveAnime } from "@/features/search/api";

interface UseToggleSavedOptions {
	id: string;
	title: string;
	initialSaved: boolean;
}

export const useToggleSaved = ({
	id,
	title,
	initialSaved,
}: UseToggleSavedOptions) => {
	const queryClient = useQueryClient();
	const [isSaved, setIsSaved] = useState(initialSaved);

	const handleError = (error: unknown) => {
		const axiosError = error as AxiosError<{ message: string }>;
		const message =
			axiosError.response?.data?.message ?? axiosError.message ?? "Error";
		toast.error(message);
	};

	const invalidate = () => {
		queryClient.invalidateQueries({ queryKey: ["animes"] });
		queryClient.invalidateQueries({ queryKey: ["users", "statistics"] });
	};

	const saveMutation = useMutation({
		mutationFn: saveAnime,
		onSuccess: () => {
			setIsSaved(true);
			invalidate();
			toast.success(`${title} saved`);
		},
		onError: handleError,
	});

	const unsaveMutation = useMutation({
		mutationFn: unsaveAnime,
		onSuccess: () => {
			setIsSaved(false);
			invalidate();
			toast.success(`${title} removed from saved`);
		},
		onError: handleError,
	});

	const toggle = () => {
		if (isSaved) {
			unsaveMutation.mutate(id);
		} else {
			saveMutation.mutate(id);
		}
	};

	return {
		isSaved,
		isPending: saveMutation.isPending || unsaveMutation.isPending,
		toggle,
	};
};

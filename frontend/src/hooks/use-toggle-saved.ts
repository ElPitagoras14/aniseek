import { useMutation } from "@tanstack/react-query";
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
	const [isSaved, setIsSaved] = useState(initialSaved);

	const handleError = (error: unknown) => {
		const axiosError = error as AxiosError<{ message: string }>;
		const message =
			axiosError.response?.data?.message ?? axiosError.message ?? "Error";
		toast.error(message);
	};

	const saveMutation = useMutation({
		mutationFn: saveAnime,
		onSuccess: () => {
			setIsSaved(true);
			toast.success(`${title} saved`);
		},
		onError: handleError,
	});

	const unsaveMutation = useMutation({
		mutationFn: unsaveAnime,
		onSuccess: () => {
			setIsSaved(false);
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

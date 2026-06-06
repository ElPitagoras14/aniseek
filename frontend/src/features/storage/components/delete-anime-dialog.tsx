import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import { formatBytes } from "@/lib/format-bytes";
import { deleteAnimeStorage } from "@/features/storage/api";
import type { StorageItem } from "@/features/storage/types";

interface DeleteAnimeDialogProps {
	anime: StorageItem;
}

export function DeleteAnimeDialog({ anime }: DeleteAnimeDialogProps) {
	const [open, setOpen] = useState(false);
	const queryClient = useQueryClient();

	const mutation = useMutation({
		mutationFn: () => deleteAnimeStorage(anime.id),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["episodes", "storage"] });
			toast.success(`"${anime.title}" eliminado`);
			setOpen(false);
		},
		onError: (error) => {
			const axiosError = error as AxiosError<{ message: string }>;
			const message =
				axiosError.response?.data?.message ?? axiosError.message ?? "Error";
			toast.error(message);
		},
	});

	return (
		<Dialog open={open} onOpenChange={setOpen}>
			<DialogTrigger asChild>
				<Button variant="ghost" size="icon" className="text-muted-foreground hover:text-destructive">
					<Trash2 className="h-4 w-4" />
				</Button>
			</DialogTrigger>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>Eliminar anime</DialogTitle>
					<DialogDescription>
						¿Eliminar <span className="font-medium text-foreground">"{anime.title}"</span> y liberar{" "}
						{formatBytes(anime.size)}? Esta acción no se puede deshacer.
					</DialogDescription>
				</DialogHeader>
				<DialogFooter>
					<Button variant="outline" onClick={() => setOpen(false)} disabled={mutation.isPending}>
						Cancelar
					</Button>
					<Button
						variant="destructive"
						onClick={() => mutation.mutate()}
						disabled={mutation.isPending}
					>
						{mutation.isPending ? "Eliminando…" : "Eliminar"}
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Spinner } from "@/components/ui/spinner";
import apiClient from "@/lib/api-client";
import { useMutation } from "@tanstack/react-query";
import { TrashIcon } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface ActionCellProps {
  animeId: string;
  title: string;
  refetch: () => Promise<void>;
}

const deleteAnimeStorage = async (animeId: string) => {
  const options = {
    method: "DELETE",
    url: `/animes/storage/${animeId}`,
  };

  await apiClient(options);
};

export default function ActionCell({
  animeId,
  title,
  refetch,
}: ActionCellProps) {
  const [open, setOpen] = useState<boolean>(false);

  const deleteMutation = useMutation({
    mutationFn: deleteAnimeStorage,
    onSuccess: async () => {
      await refetch();
      toast.success("Anime deleted successfully");
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleDeleteAnime = async () => {
    deleteMutation.mutate(animeId);
    setOpen(false);
  };

  return (
    <div className="flex justify-center">
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger>
          <TrashIcon className="text-red-500 dark:text-red-400 w-5 h-5 cursor-pointer" />
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Anime</DialogTitle>
          </DialogHeader>
          <span className="text-muted-foreground">
            Are you sure you want to delete{" "}
            <strong className="text-primary">&quot;{title}&quot;</strong>?
          </span>
          <div className="flex justify-end gap-x-4">
            <Button
              variant="outline"
              onClick={() => setOpen(false)}
              className="cursor-pointer"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              className="cursor-pointer"
              onClick={handleDeleteAnime}
            >
              {deleteMutation.isPending ? <Spinner /> : "Delete"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

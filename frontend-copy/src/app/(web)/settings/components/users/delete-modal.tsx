import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { TrashIcon } from "lucide-react";
import { useState } from "react";

interface DeleteModalProps {
  userId: string;
  username: string;
}

export default function DeleteModal({ username }: DeleteModalProps) {
  const [open, setOpen] = useState<boolean>(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger>
        <TrashIcon className="text-red-500 dark:text-red-400 w-6 h-6 cursor-pointer" />
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete User</DialogTitle>
        </DialogHeader>
        <span>
          Are you sure you want to delete{" "}
          <strong>&quot;{username}&quot;</strong>?
        </span>
        <div className="flex justify-end gap-x-4">
          <Button variant="outline" onClick={() => setOpen(false)} className="cursor-pointer">Cancel</Button>
          <Button variant="destructive" className="cursor-pointer">Delete</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

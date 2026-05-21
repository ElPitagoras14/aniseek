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

interface ActionCellProps {
  userId: string;
  username: string;
}

export default function ActionCell({ username }: ActionCellProps) {
  const [open, setOpen] = useState<boolean>(false);

  return (
    <div className="flex justify-center">
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger>
          <TrashIcon className="text-red-500 dark:text-red-400 w-5 h-5 cursor-pointer" />
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete User</DialogTitle>
          </DialogHeader>
          <span className="text-muted-foreground">
            Are you sure you want to delete{" "}
            <strong className="text-primary">&quot;{username}&quot;</strong>?
          </span>
          <div className="flex justify-end gap-x-4">
            <Button
              variant="outline"
              onClick={() => setOpen(false)}
              className="cursor-pointer"
            >
              Cancel
            </Button>
            <Button variant="destructive" className="cursor-pointer">
              Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

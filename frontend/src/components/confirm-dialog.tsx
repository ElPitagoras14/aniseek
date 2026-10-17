import { Loader2 } from "lucide-react";
import { type ReactNode, useState } from "react";
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

interface ConfirmDialogProps {
	trigger: ReactNode;
	title: string;
	description: ReactNode;
	confirmLabel: string;
	destructive?: boolean;
	// Resolves when the action is done; the dialog stays open while it runs and
	// closes once it settles.
	onConfirm: () => Promise<unknown>;
}

export function ConfirmDialog({
	trigger,
	title,
	description,
	confirmLabel,
	destructive = false,
	onConfirm,
}: ConfirmDialogProps) {
	const [open, setOpen] = useState(false);
	const [pending, setPending] = useState(false);

	const confirm = async () => {
		setPending(true);
		try {
			await onConfirm();
		} finally {
			setPending(false);
			setOpen(false);
		}
	};

	return (
		<Dialog open={open} onOpenChange={(next) => !pending && setOpen(next)}>
			<DialogTrigger asChild>{trigger}</DialogTrigger>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>{title}</DialogTitle>
					<DialogDescription>{description}</DialogDescription>
				</DialogHeader>
				<DialogFooter>
					<Button
						variant="outline"
						onClick={() => setOpen(false)}
						disabled={pending}
					>
						Cancel
					</Button>
					<Button
						variant={destructive ? "destructive" : "default"}
						onClick={confirm}
						disabled={pending}
					>
						{pending && <Loader2 className="animate-spin" />}
						{confirmLabel}
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}

import { useMutation } from "@tanstack/react-query";
import { KeyRound, Loader2 } from "lucide-react";
import { useState } from "react";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { resetUserPassword } from "@/features/access/api";
import { parseApiError } from "@/features/access/lib/parse-error";
import type { AccessUser } from "@/features/access/types";

export function ResetPasswordDialog({ user }: { user: AccessUser }) {
	const [open, setOpen] = useState(false);
	const [password, setPassword] = useState("");

	const mutation = useMutation({
		mutationFn: () => resetUserPassword(user.id, password),
		onSuccess: () => {
			toast.success(`Password of "${user.username}" updated`);
			setOpen(false);
			setPassword("");
		},
		onError: (error) => {
			toast.error(parseApiError(error, "Could not reset the password"));
		},
	});

	return (
		<Dialog open={open} onOpenChange={setOpen}>
			<DialogTrigger asChild>
				<Button
					variant="ghost"
					size="icon"
					aria-label={`Reset password of ${user.username}`}
				>
					<KeyRound />
				</Button>
			</DialogTrigger>
			<DialogContent>
				<form
					onSubmit={(e) => {
						e.preventDefault();
						mutation.mutate();
					}}
					className="flex flex-col gap-4"
				>
					<DialogHeader>
						<DialogTitle>Reset password</DialogTitle>
						<DialogDescription>
							Set a new password for{" "}
							<span className="font-medium text-foreground">
								{user.username}
							</span>
							. Their current sessions will be closed.
						</DialogDescription>
					</DialogHeader>
					<div className="flex flex-col gap-2">
						<Label htmlFor="reset-password">New password</Label>
						<Input
							id="reset-password"
							type="password"
							required
							minLength={6}
							autoComplete="new-password"
							placeholder="At least 6 characters"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							disabled={mutation.isPending}
						/>
					</div>
					<DialogFooter>
						<Button
							type="button"
							variant="outline"
							onClick={() => setOpen(false)}
							disabled={mutation.isPending}
						>
							Cancel
						</Button>
						<Button type="submit" disabled={mutation.isPending}>
							{mutation.isPending && <Loader2 className="animate-spin" />}
							Reset password
						</Button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	);
}

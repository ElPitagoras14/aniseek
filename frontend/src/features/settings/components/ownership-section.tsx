import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
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
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import {
	currentUserQueryOptions,
	transferOwner,
	usersQueryOptions,
} from "@/features/access/api";
import { parseApiError } from "@/features/access/lib/parse-error";

export function OwnershipSection() {
	const [open, setOpen] = useState(false);
	const [targetId, setTargetId] = useState("");
	const [password, setPassword] = useState("");
	const queryClient = useQueryClient();
	const users = useQuery(usersQueryOptions);
	const me = useQuery(currentUserQueryOptions);

	const candidates = (users.data?.items ?? []).filter(
		(u) => u.isActive && u.id !== me.data?.id,
	);
	const target = candidates.find((u) => u.id === targetId);

	const mutation = useMutation({
		mutationFn: transferOwner,
		onSuccess: () => {
			toast.success(`"${target?.username}" is now the owner`);
			setOpen(false);
			setPassword("");
			setTargetId("");
			// The role of both users changed: refetch who is who.
			queryClient.invalidateQueries({ queryKey: ["users"] });
		},
		onError: (error) => {
			toast.error(parseApiError(error, "Could not transfer ownership"));
		},
	});

	return (
		<div className="flex items-center gap-3">
			<Select value={targetId} onValueChange={setTargetId}>
				<SelectTrigger className="min-w-0 flex-1">
					<SelectValue placeholder="Choose the new owner" />
				</SelectTrigger>
				<SelectContent>
					{candidates.map((u) => (
						<SelectItem key={u.id} value={u.id}>
							{u.username}
						</SelectItem>
					))}
				</SelectContent>
			</Select>
			<Dialog open={open} onOpenChange={setOpen}>
				<DialogTrigger asChild>
					<Button variant="destructive" className="shrink-0" disabled={!target}>
						Transfer ownership
					</Button>
				</DialogTrigger>
				<DialogContent>
					<form
						onSubmit={(e) => {
							e.preventDefault();
							mutation.mutate({
								targetUserId: targetId,
								currentPassword: password,
							});
						}}
						className="flex flex-col gap-4"
					>
						<DialogHeader>
							<DialogTitle>Transfer ownership</DialogTitle>
							<DialogDescription>
								<span className="font-medium text-foreground">
									{target?.username}
								</span>{" "}
								will become the owner and you will become an administrator. Only
								they can undo this. Confirm with your password.
							</DialogDescription>
						</DialogHeader>
						<div className="flex flex-col gap-2">
							<Label htmlFor="transfer-password">Your password</Label>
							<Input
								id="transfer-password"
								type="password"
								required
								autoComplete="current-password"
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
							<Button
								type="submit"
								variant="destructive"
								disabled={mutation.isPending}
							>
								{mutation.isPending && <Loader2 className="animate-spin" />}
								Transfer
							</Button>
						</DialogFooter>
					</form>
				</DialogContent>
			</Dialog>
		</div>
	);
}

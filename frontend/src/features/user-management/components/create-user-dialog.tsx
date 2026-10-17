import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2, UserPlus } from "lucide-react";
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
import { createUser, usersQueryOptions } from "@/features/access/api";
import { parseApiError } from "@/features/access/lib/parse-error";
import type { AccessUser, Role } from "@/features/access/types";

export function CreateUserDialog({ me }: { me: AccessUser }) {
	const [open, setOpen] = useState(false);
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [role, setRole] = useState<Role>("member");
	const queryClient = useQueryClient();

	const mutation = useMutation({
		mutationFn: createUser,
		onSuccess: (user) => {
			queryClient.invalidateQueries({ queryKey: usersQueryOptions.queryKey });
			toast.success(`User "${user.username}" created`);
			setOpen(false);
			setUsername("");
			setPassword("");
			setRole("member");
		},
		onError: (error) => {
			toast.error(parseApiError(error, "Could not create the user"));
		},
	});

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		mutation.mutate({ username: username.trim(), password, role });
	};

	return (
		<Dialog open={open} onOpenChange={setOpen}>
			<DialogTrigger asChild>
				<Button>
					<UserPlus />
					Create user
				</Button>
			</DialogTrigger>
			<DialogContent>
				<form onSubmit={handleSubmit} className="flex flex-col gap-4">
					<DialogHeader>
						<DialogTitle>Create user</DialogTitle>
						<DialogDescription>
							The account is created active and works with any registration
							policy.
						</DialogDescription>
					</DialogHeader>
					<div className="flex flex-col gap-2">
						<Label htmlFor="new-username">Username</Label>
						<Input
							id="new-username"
							required
							maxLength={64}
							autoComplete="off"
							value={username}
							onChange={(e) => setUsername(e.target.value)}
							disabled={mutation.isPending}
						/>
					</div>
					<div className="flex flex-col gap-2">
						<Label htmlFor="new-password">Password</Label>
						<Input
							id="new-password"
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
					{me.role === "owner" && (
						<div className="flex flex-col gap-2">
							<Label>Role</Label>
							<Select value={role} onValueChange={(v) => setRole(v as Role)}>
								<SelectTrigger className="w-full">
									<SelectValue />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="member">Member</SelectItem>
									<SelectItem value="admin">Administrator</SelectItem>
								</SelectContent>
							</Select>
						</div>
					)}
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
							Create
						</Button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	);
}

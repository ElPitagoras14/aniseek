import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, Copy, Loader2, MailPlus } from "lucide-react";
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
	createInvitation,
	invitationsQueryOptions,
} from "@/features/access/api";
import { parseApiError } from "@/features/access/lib/parse-error";
import type { AccessUser, Role } from "@/features/access/types";
import { copyText } from "@/lib/clipboard";

const MAX_DAYS = 30;

export function CreateInvitationDialog({ me }: { me: AccessUser }) {
	const [open, setOpen] = useState(false);
	const [role, setRole] = useState<Role>("member");
	const [days, setDays] = useState(7);
	// The token is only ever returned by the create call: keep it here, show
	// it once and drop it when the dialog closes.
	const [link, setLink] = useState<string | null>(null);
	const [copied, setCopied] = useState(false);
	const queryClient = useQueryClient();

	const mutation = useMutation({
		mutationFn: createInvitation,
		onSuccess: (invitation) => {
			queryClient.invalidateQueries({
				queryKey: invitationsQueryOptions.queryKey,
			});
			setLink(`${window.location.origin}/register?invite=${invitation.token}`);
		},
		onError: (error) => {
			toast.error(parseApiError(error, "Could not create the invitation"));
		},
	});

	const handleOpenChange = (next: boolean) => {
		setOpen(next);
		if (!next) {
			setLink(null);
			setCopied(false);
			setRole("member");
			setDays(7);
		}
	};

	const copy = async () => {
		if (!link) return;
		try {
			await copyText(link);
			setCopied(true);
		} catch {
			toast.error("Could not copy. Select the link and copy it manually.");
		}
	};

	return (
		<Dialog open={open} onOpenChange={handleOpenChange}>
			<DialogTrigger asChild>
				<Button>
					<MailPlus />
					Create invitation
				</Button>
			</DialogTrigger>
			<DialogContent>
				{link ? (
					<div className="flex flex-col gap-4">
						<DialogHeader>
							<DialogTitle>Invitation ready</DialogTitle>
							<DialogDescription>
								Copy the link now: it will not be shown again.
							</DialogDescription>
						</DialogHeader>
						<div className="flex gap-2">
							<Input readOnly value={link} onFocus={(e) => e.target.select()} />
							<Button
								type="button"
								variant="outline"
								size="icon"
								onClick={copy}
								aria-label="Copy link"
							>
								{copied ? <Check /> : <Copy />}
							</Button>
						</div>
						<DialogFooter>
							<Button onClick={() => handleOpenChange(false)}>Done</Button>
						</DialogFooter>
					</div>
				) : (
					<form
						onSubmit={(e) => {
							e.preventDefault();
							mutation.mutate({ role, expiresInDays: days });
						}}
						className="flex flex-col gap-4"
					>
						<DialogHeader>
							<DialogTitle>Create invitation</DialogTitle>
							<DialogDescription>
								A single-use link that works with any registration policy.
							</DialogDescription>
						</DialogHeader>
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
						<div className="flex flex-col gap-2">
							<Label htmlFor="invite-days">Expires in (days)</Label>
							<Input
								id="invite-days"
								type="number"
								min={1}
								max={MAX_DAYS}
								required
								value={days}
								onChange={(e) => setDays(Number(e.target.value))}
								disabled={mutation.isPending}
							/>
							<p className="text-xs text-muted-foreground">
								Between 1 and {MAX_DAYS} days.
							</p>
						</div>
						<DialogFooter>
							<Button
								type="button"
								variant="outline"
								onClick={() => handleOpenChange(false)}
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
				)}
			</DialogContent>
		</Dialog>
	);
}

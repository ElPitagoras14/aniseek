import { useAuth } from "@/auth";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";

export function LogoutDialog({
	open,
	onOpenChange,
}: {
	open: boolean;
	onOpenChange: (open: boolean) => void;
}) {
	const { logout } = useAuth();

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>Sign out</DialogTitle>
					<DialogDescription>
						Are you sure you want to sign out? You'll need to sign in again to
						access your account.
					</DialogDescription>
				</DialogHeader>
				<DialogFooter>
					<Button variant="outline" onClick={() => onOpenChange(false)}>
						Cancel
					</Button>
					<Button variant="destructive" onClick={logout}>
						Sign out
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}

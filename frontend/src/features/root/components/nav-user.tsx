import { LogOut, UserRound } from "lucide-react";
import { useState } from "react";
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
import {
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar";

export function NavUser() {
	const { user, logout } = useAuth();
	const [isLogoutOpen, setIsLogoutOpen] = useState(false);

	return (
		<SidebarMenu>
			<SidebarMenuItem>
				<SidebarMenuButton
					size="lg"
					className="hover:bg-white/0 active:bg-white/0"
					asChild
				>
					<div>
						<div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
							<UserRound className="size-4" />
						</div>
						<div className="grid flex-1 text-left text-sm leading-tight">
							<span className="truncate font-medium">{user?.username}</span>
							<span className="truncate text-xs">{user?.role}</span>
						</div>
						<Button
							variant="ghost"
							size="icon"
							onClick={(e) => {
								e.stopPropagation();
								setIsLogoutOpen(true);
							}}
						>
							<LogOut className="size-4" />
						</Button>
					</div>
				</SidebarMenuButton>

				<Dialog open={isLogoutOpen} onOpenChange={setIsLogoutOpen}>
					<DialogContent>
						<DialogHeader>
							<DialogTitle>Sign out</DialogTitle>
							<DialogDescription>
								Are you sure you want to sign out? You'll need to sign in again
								to access your account.
							</DialogDescription>
						</DialogHeader>
						<DialogFooter>
							<Button variant="outline" onClick={() => setIsLogoutOpen(false)}>
								Cancel
							</Button>
							<Button variant="destructive" onClick={logout}>
								Sign out
							</Button>
						</DialogFooter>
					</DialogContent>
				</Dialog>
			</SidebarMenuItem>
		</SidebarMenu>
	);
}

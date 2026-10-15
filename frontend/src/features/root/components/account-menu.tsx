import { Link } from "@tanstack/react-router";
import { LogOut, UserRound } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/auth";
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { accountNavigationData } from "../sidebar-data";
import { LogoutDialog } from "./logout-dialog";

export function AccountMenu() {
	const { user } = useAuth();
	const [isLogoutOpen, setIsLogoutOpen] = useState(false);

	return (
		<>
			{/* Non-modal so the menu fully releases focus before the logout dialog opens */}
			<DropdownMenu modal={false}>
				<DropdownMenuTrigger asChild>
					<Button
						variant="ghost"
						size="icon"
						className="rounded-full"
						aria-label="Account menu"
					>
						<span className="flex aspect-square size-8 items-center justify-center rounded-full bg-sidebar-primary text-sidebar-primary-foreground">
							<UserRound className="size-4" />
						</span>
					</Button>
				</DropdownMenuTrigger>
				<DropdownMenuContent align="end" className="min-w-48">
					<DropdownMenuLabel className="grid text-sm leading-tight">
						<span className="truncate font-medium">{user?.username}</span>
						<span className="truncate text-xs font-normal text-muted-foreground">
							{user?.role}
						</span>
					</DropdownMenuLabel>
					<DropdownMenuSeparator />
					{accountNavigationData.map((section) => (
						<DropdownMenuItem key={section.title} asChild>
							<Link to={section.url}>
								<section.icon />
								<span>{section.title}</span>
							</Link>
						</DropdownMenuItem>
					))}
					<DropdownMenuSeparator />
					<DropdownMenuItem
						variant="destructive"
						onSelect={() => setIsLogoutOpen(true)}
					>
						<LogOut />
						<span>Sign out</span>
					</DropdownMenuItem>
				</DropdownMenuContent>
			</DropdownMenu>

			<LogoutDialog open={isLogoutOpen} onOpenChange={setIsLogoutOpen} />
		</>
	);
}

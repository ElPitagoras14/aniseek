import { LogOut, UserRound } from "lucide-react";
import { useState } from "react";
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
import {
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar";

export function NavUser() {
	// const navigate = Route.useNavigate();
	// const location = useLocation({ select: (l) => l.href });
	const [isLogoutOpen, setIsLogoutOpen] = useState(false);

	const user = {
		username: "aniseek",
		role: "admin",
	};

	// const handleLogout = async () => {
	// 	await auth.logout();
	// 	navigate({ to: "/login", search: { redirect: location }, replace: true });
	// };

	return (
		<SidebarMenu>
			<SidebarMenuItem>
				<Dialog open={isLogoutOpen} onOpenChange={setIsLogoutOpen}>
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
								<span className="truncate font-medium">{user.username}</span>
								<span className="truncate text-xs">{user.role}</span>
							</div>
							<DialogTrigger asChild>
								<div>
									<Button variant="ghost" size="icon">
										<LogOut className="size-4" />
									</Button>
								</div>
							</DialogTrigger>
						</div>
					</SidebarMenuButton>
					<DialogContent>
						<DialogHeader>
							<DialogTitle>Cerrar Sesión</DialogTitle>
							<DialogDescription>
								¿Estás seguro de que quieres cerrar sesión? Tendrás que iniciar
								sesión nuevamente para acceder a tu cuenta.
							</DialogDescription>
						</DialogHeader>
						<DialogFooter>
							<Button variant="outline" onClick={() => setIsLogoutOpen(false)}>
								Cancelar
							</Button>
							<Button variant="destructive">Cerrar Sesión</Button>
						</DialogFooter>
					</DialogContent>
				</Dialog>
			</SidebarMenuItem>
		</SidebarMenu>
	);
}

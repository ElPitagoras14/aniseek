import { Link, useMatchRoute } from "@tanstack/react-router";
import {
	SidebarGroup,
	SidebarGroupContent,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar";
import { useCurrentUser } from "@/features/access/hooks/use-current-user";
import { isVisibleTo, type NavSection } from "../sidebar-data";

export function NavSecondary({
	items,
	...props
}: { items: NavSection[] } & React.ComponentPropsWithoutRef<
	typeof SidebarGroup
>) {
	const matchRoute = useMatchRoute();
	const { data: currentUser } = useCurrentUser();

	return (
		<SidebarGroup {...props}>
			<SidebarGroupContent>
				<SidebarMenu>
					{items
						.filter((item) => isVisibleTo(item, currentUser?.role))
						.map((item) => (
							<SidebarMenuItem key={item.title}>
								<SidebarMenuButton
									asChild
									disabled={item.disabled}
									isActive={!!matchRoute({ to: item.url, fuzzy: true })}
								>
									<Link to={item.url}>
										<item.icon />
										<span>{item.title}</span>
									</Link>
								</SidebarMenuButton>
							</SidebarMenuItem>
						))}
				</SidebarMenu>
			</SidebarGroupContent>
		</SidebarGroup>
	);
}

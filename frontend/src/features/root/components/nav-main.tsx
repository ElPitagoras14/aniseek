import { Link, useMatchRoute } from "@tanstack/react-router";
import {
	SidebarGroup,
	SidebarGroupLabel,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar";
import { useCurrentUser } from "@/features/access/hooks/use-current-user";
import { isVisibleTo, type NavGroup, type NavSection } from "../sidebar-data";

export function NavMain({ groups }: { groups: NavGroup[] }) {
	const matchRoute = useMatchRoute();
	const { data: currentUser } = useCurrentUser();

	return groups?.map((group: NavGroup) => (
		<SidebarGroup key={group.title}>
			<SidebarGroupLabel>{group.title}</SidebarGroupLabel>
			<SidebarMenu>
				{group.sections
					.filter((section) => isVisibleTo(section, currentUser?.role))
					.map((section: NavSection) => (
						<SidebarMenuItem key={section.title}>
							<SidebarMenuButton
								asChild
								className="cursor-pointer"
								disabled={section.disabled}
								isActive={!!matchRoute({ to: section.url, fuzzy: true })}
							>
								<Link to={section.url}>
									{section.icon && <section.icon />}
									<span>{section.title}</span>
								</Link>
							</SidebarMenuButton>
						</SidebarMenuItem>
					))}
			</SidebarMenu>
		</SidebarGroup>
	));
}

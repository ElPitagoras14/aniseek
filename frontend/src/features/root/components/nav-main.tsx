import { Link } from "@tanstack/react-router";
import {
	SidebarGroup,
	SidebarGroupLabel,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar";
import type { NavGroup, NavSection } from "../sidebar-data";

export function NavMain({ groups }: { groups: NavGroup[] }) {
	return groups?.map((group: NavGroup) => (
		<SidebarGroup key={group.title}>
			<SidebarGroupLabel>{group.title}</SidebarGroupLabel>
			<SidebarMenu>
				{group.sections.map((section: NavSection) => (
					<SidebarMenuItem key={section.title}>
						<SidebarMenuButton asChild className="cursor-pointer">
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

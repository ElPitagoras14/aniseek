import {
	Bookmark,
	Calendar,
	Database,
	Download,
	Folder,
	Home,
	type LucideIcon,
	Search,
	Settings,
	UserRound,
	Users,
} from "lucide-react";
import { hasRole } from "@/features/access/lib/roles";
import type { Role } from "@/features/access/types";

export type NavSection = {
	title: string;
	icon: LucideIcon;
	url: string;
	disabled?: boolean;
	// Where the section lives below the mobile breakpoint; omitted = hidden on mobile
	mobile?: "bottom" | "account";
	// Hidden below this role. Only a convenience: the backend enforces.
	minRole?: Role;
};

export type NavGroup = {
	title: string;
	sections: NavSection[];
};

const animeSection: NavSection[] = [
	{
		title: "Home",
		mobile: "bottom",
		icon: Home,
		url: "/home",
	},
	{
		title: "Search",
		mobile: "bottom",
		icon: Search,
		url: "/search",
	},
	{
		title: "Saved",
		mobile: "bottom",
		icon: Bookmark,
		url: "/saved",
	},
	{
		title: "Calendar",
		mobile: "bottom",
		icon: Calendar,
		url: "/calendar",
	},
	{
		title: "Downloads",
		mobile: "bottom",
		icon: Download,
		url: "/downloads",
	},
];

const administrationSection: NavSection[] = [
	{
		title: "Franchises",
		icon: Folder,
		url: "/franchises",
		disabled: true,
	},
	{
		title: "Storage",
		mobile: "account",
		icon: Database,
		url: "/storage",
	},
	{
		title: "User Management",
		mobile: "account",
		icon: Users,
		url: "/user-management",
		minRole: "admin",
	},
];

export const mainNavigationData: NavGroup[] = [
	{
		title: "Anime",
		sections: animeSection,
	},
	{
		title: "Administration",
		sections: administrationSection,
	},
];

export const secondaryNavigationData: NavSection[] = [
	{
		title: "Instance Settings",
		mobile: "account",
		icon: Settings,
		url: "/instance-settings",
		minRole: "admin",
	},
	{
		title: "Profile",
		mobile: "account",
		icon: UserRound,
		url: "/profile",
	},
];

const mainSections: NavSection[] = mainNavigationData.flatMap(
	(group) => group.sections,
);

export const bottomNavigationData: NavSection[] = mainSections.filter(
	(section) => section.mobile === "bottom",
);

export const accountNavigationData: NavSection[] = [
	...secondaryNavigationData,
	...mainSections,
].filter((section) => section.mobile === "account");

export function isVisibleTo(section: NavSection, role: string | undefined) {
	return !section.minRole || hasRole(role, section.minRole);
}

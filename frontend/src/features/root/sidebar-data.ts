import {
	Bookmark,
	Calendar,
	Database,
	Download,
	Folder,
	Home,
	type LucideIcon,
	Search,
	UserRound,
} from "lucide-react";

export type NavSection = {
	title: string;
	icon: LucideIcon;
	url: string;
	disabled?: boolean;
};

export type NavGroup = {
	title: string;
	sections: NavSection[];
};

const animeSection: NavSection[] = [
	{
		title: "Home",
		icon: Home,
		url: "/home",
	},
	{
		title: "Search",
		icon: Search,
		url: "/search",
	},
	{
		title: "Saved",
		icon: Bookmark,
		url: "/saved",
	},
	{
		title: "Calendar",
		icon: Calendar,
		url: "/calendar",
	},
	{
		title: "Downloads",
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
		icon: Database,
		url: "/storage",
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
		title: "Profile",
		icon: UserRound,
		url: "/profile",
	},
];

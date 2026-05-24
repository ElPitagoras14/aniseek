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
    disabled: true,
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
    disabled: true,
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
    title: "Configuration",
    icon: Settings,
    url: "/profile",
    disabled: true,
  },
];

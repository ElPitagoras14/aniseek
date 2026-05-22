import {
  Bookmark,
  Calendar,
  Database,
  Download,
  Folder,
  type LucideIcon,
  Search,
  Settings,
} from "lucide-react";

export type NavSection = {
  title: string;
  icon: LucideIcon;
  url: string;
};

export type NavGroup = {
  title: string;
  sections: NavSection[];
};

const animeSection: NavSection[] = [
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
    url: "/administration/franchises",
  },
  {
    title: "Storage",
    icon: Database,
    url: "/administration/storage",
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
    title: "Configuración",
    icon: Settings,
    url: "/settings",
  },
];

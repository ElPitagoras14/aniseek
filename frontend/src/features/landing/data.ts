import {
	ArrowDownToLine,
	Bookmark,
	CalendarDays,
	Globe,
	HardDrive,
	LayoutDashboard,
	type LucideIcon,
	Search,
} from "lucide-react";

export interface LandingFeature {
	icon: LucideIcon;
	title: string;
	description: string;
	iconClassName: string;
}

export interface LandingStep {
	number: number;
	icon: LucideIcon;
	iconClassName: string;
	title: string;
	description: string;
}

export const LANDING_FEATURES: LandingFeature[] = [
	{
		icon: Search,
		title: "Search & Discovery",
		description:
			"Find any anime instantly across multiple sources with a unified search. Get cover art, synopses, genres, and episode counts in one place.",
		iconClassName: "text-sky-500",
	},
	{
		icon: ArrowDownToLine,
		title: "Episode Downloads",
		description:
			"Queue and download episodes directly to your device. Track progress in real time and resume interrupted downloads without losing your place.",
		iconClassName: "text-emerald-500",
	},
	{
		icon: CalendarDays,
		title: "Airing Calendar",
		description:
			"Never miss a new episode. The airing calendar shows exactly when your favourite series drop new episodes, sorted by day of the week.",
		iconClassName: "text-amber-500",
	},
	{
		icon: Bookmark,
		title: "Saved Collections",
		description:
			"Bookmark anime you want to watch later and organise your personal library. Pick up right where you left off at any time.",
		iconClassName: "text-indigo-500",
	},
	{
		icon: HardDrive,
		title: "Storage Management",
		description:
			"See exactly how much space each series occupies on your device. Delete episodes you've already watched to free up storage in seconds.",
		iconClassName: "text-violet-500",
	},
	{
		icon: Globe,
		title: "Multi-Source Support",
		description:
			"AniSeek aggregates content from AnimeFLV, JKAnime, and AnimeAV1 so you always have a working mirror, even when one source goes down.",
		iconClassName: "text-rose-500",
	},
];

export const LANDING_STEPS: LandingStep[] = [
	{
		number: 1,
		icon: Search,
		iconClassName: "text-sky-500",
		title: "Search",
		description:
			"Type any title and instantly browse results from all supported sources. Filter by genre, status, or airing schedule.",
	},
	{
		number: 2,
		icon: ArrowDownToLine,
		iconClassName: "text-emerald-500",
		title: "Download",
		description:
			"Pick the episode and quality you want. AniSeek resolves the real download link and saves the file directly to your device.",
	},
	{
		number: 3,
		icon: LayoutDashboard,
		iconClassName: "text-violet-500",
		title: "Manage",
		description:
			"Track what you've downloaded, follow airing schedules, and manage your storage. All from a single clean dashboard.",
	},
];

export const LANDING_SOURCES = ["AnimeFLV", "JKAnime", "AnimeAV1"] as const;

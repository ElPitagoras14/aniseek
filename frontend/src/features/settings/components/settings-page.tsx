import { Navigate } from "@tanstack/react-router";
import { Bot, Crown, UserPlus } from "lucide-react";
import { type PageSection, SectionedPage } from "@/components/sectioned-page";
import { Skeleton } from "@/components/ui/skeleton";
import { isAuthEnabled } from "@/config";
import { useCurrentUser } from "@/features/access/hooks/use-current-user";
import { hasRole } from "@/features/access/lib/roles";
import type { Role } from "@/features/access/types";
import { McpSection } from "./mcp-section";
import { OwnershipSection } from "./ownership-section";
import { RegistrationSection } from "./registration-section";

interface SettingsSectionDef extends PageSection {
	minRole: Role;
	// Shown in single-user mode too. Without a login, registration has no
	// effect and a transfer cannot confirm a password.
	singleUser: boolean;
}

const SECTIONS: SettingsSectionDef[] = [
	{
		id: "registration",
		label: "Registration",
		icon: UserPlus,
		description: "Who can sign up without an invitation.",
		content: <RegistrationSection />,
		minRole: "admin",
		singleUser: false,
	},
	{
		id: "mcp",
		label: "MCP server",
		icon: Bot,
		description:
			"Let AI agents search, organize and download anime over the Model Context Protocol.",
		content: <McpSection />,
		minRole: "owner",
		singleUser: true,
	},
	{
		id: "ownership",
		label: "Ownership",
		icon: Crown,
		description: "Make another user the owner. You become an administrator.",
		content: <OwnershipSection />,
		minRole: "owner",
		singleUser: false,
		tone: "danger",
	},
];

export function SettingsPage() {
	const { data: me, isLoading } = useCurrentUser();

	if (isLoading) {
		return (
			<div className="p-4 md:p-6">
				<Skeleton className="h-8 w-48" />
			</div>
		);
	}
	// The backend rejects these calls anyway; this just keeps members out of
	// a page that cannot work for them.
	if (!me || !hasRole(me.role, "admin")) {
		return <Navigate to="/home" replace />;
	}

	const sections = SECTIONS.filter(
		(s) => hasRole(me.role, s.minRole) && (isAuthEnabled || s.singleUser),
	);

	return (
		<SectionedPage
			title="Instance Settings"
			description="Configure how this instance works"
			navLabel="Instance settings sections"
			sections={sections}
		/>
	);
}

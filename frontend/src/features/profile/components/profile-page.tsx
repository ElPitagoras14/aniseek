import { Bot, Lock, UserRound } from "lucide-react";
import { type PageSection, SectionedPage } from "@/components/sectioned-page";
import { isAuthEnabled } from "@/config";
import { ApiKeySection } from "./api-key-section";
import { McpConnection } from "./mcp-connection";
import { PasswordSection } from "./password-section";
import { ProfileHeader } from "./profile-header";
import { UsernameSection } from "./username-section";

const SECTIONS: PageSection[] = [
	{
		id: "account",
		label: "Account",
		icon: UserRound,
		description: "Your account information",
		content: (
			<div className="flex flex-col gap-1.5">
				<p className="text-sm">Username</p>
				<UsernameSection />
			</div>
		),
	},
	// Single-user mode has no login, so a password would be unused.
	...(isAuthEnabled
		? [
				{
					id: "security",
					label: "Security",
					icon: Lock,
					description: "Change your password",
					content: <PasswordSection />,
				},
			]
		: []),
	{
		id: "ai-agents",
		label: "AI agents",
		icon: Bot,
		description:
			"Connect AI agents over MCP. They act as you, with your current role's permissions.",
		content: (
			<div className="flex flex-col gap-6">
				<div className="flex flex-col gap-2">
					<p className="text-sm font-medium">API key</p>
					<ApiKeySection />
				</div>
				<McpConnection />
			</div>
		),
	},
];

export function ProfilePage() {
	return (
		<SectionedPage
			title="Profile"
			description="Manage your account settings and security"
			aside={<ProfileHeader />}
			navLabel="Profile sections"
			sections={SECTIONS}
		/>
	);
}

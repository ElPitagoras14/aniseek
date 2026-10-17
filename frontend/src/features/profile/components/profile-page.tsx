import { KeyRound, Lock, type LucideIcon, UserRound } from "lucide-react";
import { Fragment, type ReactNode, useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { isAuthEnabled } from "@/config";
import { cn } from "@/lib/utils";
import { ApiKeySection } from "./api-key-section";
import { PasswordSection } from "./password-section";
import { ProfileHeader } from "./profile-header";
import { UsernameSection } from "./username-section";

interface SectionDef {
	id: string;
	label: string;
	icon: LucideIcon;
	description: string;
	content: ReactNode;
}

const SECTIONS: SectionDef[] = [
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
		id: "api-key",
		label: "API key",
		icon: KeyRound,
		description:
			"Lets AI agents connect over MCP and act as you, with your current role's permissions.",
		content: <ApiKeySection />,
	},
];

function scrollToSection(id: string) {
	document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
	// The hash makes the section linkable (/profile#api-key) without a
	// router navigation.
	window.history.replaceState(null, "", `#${id}`);
}

// Highlights the section in view: the last one whose top has passed a line
// near the top of the viewport. At the end of the page it is the last
// section, which is often too short to ever reach that line.
function useActiveSection(ids: string[]) {
	const [active, setActive] = useState(ids[0]);

	useEffect(() => {
		const update = (event?: Event) => {
			const target = event?.target;
			const scroller =
				target instanceof HTMLElement
					? target
					: (document.scrollingElement as HTMLElement);
			const atBottom =
				scroller.scrollTop + scroller.clientHeight >= scroller.scrollHeight - 2;
			if (atBottom && scroller.scrollTop > 0) {
				setActive(ids[ids.length - 1]);
				return;
			}
			const line = window.innerHeight * 0.25;
			let current = ids[0];
			for (const id of ids) {
				const top = document.getElementById(id)?.getBoundingClientRect().top;
				if (top !== undefined && top <= line) current = id;
			}
			setActive(current);
		};
		// Capture, so it also catches scrolling inside the app shell's container.
		document.addEventListener("scroll", update, {
			capture: true,
			passive: true,
		});
		return () =>
			document.removeEventListener("scroll", update, { capture: true });
	}, [ids]);

	return [active, setActive] as const;
}

const SECTION_IDS = SECTIONS.map((s) => s.id);

export function ProfilePage() {
	const [active, setActive] = useActiveSection(SECTION_IDS);

	// Opening /profile#api-key lands on that section.
	useEffect(() => {
		const id = window.location.hash.slice(1);
		if (SECTION_IDS.includes(id)) {
			document.getElementById(id)?.scrollIntoView();
			setActive(id);
		}
	}, [setActive]);

	return (
		<div className="mx-auto flex w-full max-w-5xl flex-col gap-6 p-4 md:p-6 lg:p-8">
			<div>
				<h1 className="text-2xl font-bold">Profile</h1>
				<p className="text-sm text-muted-foreground">
					Manage your account settings and security
				</p>
			</div>

			<div className="grid gap-6 md:grid-cols-[220px_1fr]">
				<aside className="flex min-w-0 flex-col gap-5 self-start md:sticky md:top-6">
					<ProfileHeader />
					<nav
						aria-label="Profile sections"
						className="flex gap-1 overflow-x-auto md:flex-col"
					>
						{SECTIONS.map(({ id, label, icon: Icon }) => (
							<button
								key={id}
								type="button"
								onClick={() => {
									setActive(id);
									scrollToSection(id);
								}}
								aria-current={id === active ? "true" : undefined}
								className={cn(
									"flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
									id === active
										? "bg-muted font-medium text-foreground"
										: "text-muted-foreground hover:bg-muted/50 hover:text-foreground",
								)}
							>
								<Icon className="size-4" />
								{label}
							</button>
						))}
					</nav>
				</aside>

				<Card className="min-w-0">
					<CardContent className="flex flex-col p-6">
						{SECTIONS.map(({ id, label, description, content }, index) => (
							<Fragment key={id}>
								{index > 0 && <Separator className="my-6" />}
								<section id={id} className="flex scroll-mt-6 flex-col gap-5">
									<div>
										<h2 className="text-lg font-semibold">{label}</h2>
										<p className="text-sm text-muted-foreground">
											{description}
										</p>
									</div>
									{content}
								</section>
							</Fragment>
						))}
					</CardContent>
				</Card>
			</div>
		</div>
	);
}

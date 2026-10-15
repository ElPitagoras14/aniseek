import { Link } from "@tanstack/react-router";
import { bottomNavigationData } from "../sidebar-data";

// Shown below `md` (768px), the same cut as MOBILE_BREAKPOINT in
// hooks/use-mobile.ts that the sidebar uses: keep both in sync.
export function BottomNav() {
	return (
		<nav
			aria-label="Main"
			// Top rule drawn as an inset shadow so the bar stays exactly h-16 (AppShell reserves 4rem)
			className="fixed inset-x-0 bottom-0 z-40 bg-background/95 pb-[env(safe-area-inset-bottom)] shadow-[inset_0_1px_0_var(--color-border)] backdrop-blur-sm md:hidden"
		>
			<ul className="grid h-16 grid-cols-5">
				{bottomNavigationData.map((section) => (
					<li key={section.title}>
						<Link
							to={section.url}
							className="group flex h-full flex-col items-center justify-center gap-1 text-[11px] font-medium text-muted-foreground transition-colors"
							activeProps={{ className: "text-foreground" }}
						>
							<span className="flex h-7 w-12 items-center justify-center rounded-full transition-colors group-data-[status=active]:bg-sidebar-accent">
								<section.icon className="size-5" />
							</span>
							<span>{section.title}</span>
						</Link>
					</li>
				))}
			</ul>
		</nav>
	);
}

import { Command } from "lucide-react";
import { AccountMenu } from "./account-menu";

export function MobileHeader() {
	return (
		<header className="sticky top-0 z-10 border-b bg-background pt-[env(safe-area-inset-top)] md:hidden">
			<div className="flex h-14 items-center justify-between gap-3 px-4">
				<div className="flex items-center gap-2">
					<div className="flex aspect-square size-6 items-center justify-center rounded-md bg-sidebar-primary text-sidebar-primary-foreground">
						<Command className="size-3.5" />
					</div>
					<span className="font-medium text-sm">AniSeek</span>
				</div>
				<AccountMenu />
			</div>
		</header>
	);
}

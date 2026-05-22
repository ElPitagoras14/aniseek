import { Command } from "lucide-react";
import { SidebarTrigger } from "@/components/ui/sidebar";

export function MobileHeader() {
	return (
		<header className="sticky top-0 z-10 flex h-14 items-center gap-3 border-b bg-background px-4 md:hidden">
			<SidebarTrigger />
			<div className="flex items-center gap-2">
				<div className="flex aspect-square size-6 items-center justify-center rounded-md bg-sidebar-primary text-sidebar-primary-foreground">
					<Command className="size-3.5" />
				</div>
				<span className="font-medium text-sm">AniSeek</span>
			</div>
		</header>
	);
}

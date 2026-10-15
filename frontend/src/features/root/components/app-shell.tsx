import type { ReactNode } from "react";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppSidebar } from "./app-sidebar";
import { BottomNav } from "./bottom-nav";
import { MobileHeader } from "./mobile-header";

export function AppShell({ children }: { children: ReactNode }) {
	return (
		<SidebarProvider>
			<TooltipProvider>
				<AppSidebar variant="sidebar" />
				<SidebarInset>
					<MobileHeader />
					{/* Reserve room for the fixed bottom nav (h-16) plus the safe area */}
					<div className="flex flex-1 flex-col pb-[calc(4rem+env(safe-area-inset-bottom))] md:pb-0">
						{children}
					</div>
					<BottomNav />
				</SidebarInset>
			</TooltipProvider>
		</SidebarProvider>
	);
}

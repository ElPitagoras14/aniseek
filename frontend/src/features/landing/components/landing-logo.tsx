import { Command } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface LandingLogoProps {
	showBadge?: boolean;
	className?: string;
}

export function LandingLogo({ showBadge, className }: LandingLogoProps) {
	return (
		<div className={cn("flex items-center gap-2", className)}>
			<div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
				<Command className="size-4" />
			</div>
			<span className="font-semibold text-base">AniSeek</span>
			{showBadge && <Badge variant="secondary">Beta</Badge>}
		</div>
	);
}

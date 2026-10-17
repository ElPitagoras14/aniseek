import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface SettingsSectionProps {
	icon: LucideIcon;
	title: string;
	description: string;
	tone?: "default" | "danger";
	children: ReactNode;
}

export function SettingsSection({
	icon: Icon,
	title,
	description,
	tone = "default",
	children,
}: SettingsSectionProps) {
	const danger = tone === "danger";

	return (
		<Card className={cn("py-5", danger && "border-destructive/30")}>
			<CardContent className="flex flex-col gap-8 px-4 py-0">
				<div className="flex items-start gap-4">
					<div
						className={cn(
							"flex size-10 shrink-0 items-center justify-center rounded-lg",
							danger
								? "bg-destructive/10 text-destructive"
								: "bg-primary/10 text-primary",
						)}
					>
						<Icon className="size-5" />
					</div>
					<div className="flex min-w-0 flex-col gap-1">
						<h2 className="text-base font-semibold leading-none">{title}</h2>
						<p className="text-sm text-muted-foreground">{description}</p>
					</div>
				</div>
				<div className="flex min-w-0 flex-col gap-3">{children}</div>
			</CardContent>
		</Card>
	);
}

import type { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface HomeKpiProps {
	className?: string;
	label: string;
	value: number | undefined;
	isLoading: boolean;
	isError?: boolean;
	icon: LucideIcon;
	iconClassName?: string;
}

export function HomeKpi({
	className,
	label,
	value,
	isLoading,
	isError = false,
	icon: Icon,
	iconClassName,
}: HomeKpiProps) {
	return (
		<Card className={cn("h-full", className)}>
			<CardContent className="flex flex-col gap-3">
				<div className="flex items-center gap-2">
					<Icon className={cn("size-4", iconClassName)} />
					<span className="text-xs uppercase tracking-wide text-muted-foreground">
						{label}
					</span>
				</div>
				{isError ? (
					<span className="text-sm text-destructive">—</span>
				) : isLoading ? (
					<Skeleton className="h-9 w-20" />
				) : (
					<span className="text-3xl font-bold">{value ?? 0}</span>
				)}
			</CardContent>
		</Card>
	);
}

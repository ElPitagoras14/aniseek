import { useAuth } from "@/auth";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

interface HomeWelcomeProps {
	className?: string;
}

export function HomeWelcome({ className }: HomeWelcomeProps) {
	const { user } = useAuth();
	const username = user?.username ?? "there";
	const role = user?.role ?? "user";
	const longDate = new Intl.DateTimeFormat("en-US", {
		dateStyle: "full",
	}).format(new Date());

	return (
		<Card className={className}>
			<CardContent className="flex flex-col gap-1">
				<div className="flex items-center gap-2 min-w-0">
					<span className="text-lg font-semibold truncate">
						Welcome back, {username}
					</span>
					<Badge variant="secondary" className="capitalize shrink-0">
						{role}
					</Badge>
				</div>
				<span className="text-xs text-muted-foreground truncate">
					{longDate}
				</span>
			</CardContent>
		</Card>
	);
}

import { Skeleton } from "@/components/ui/skeleton";

export function HomeKpiSkeleton() {
	return (
		<div className="rounded-xl ring-1 ring-foreground/10 bg-card p-4 flex flex-col gap-3 h-full">
			<div className="flex items-center gap-2">
				<Skeleton className="size-4 rounded" />
				<Skeleton className="h-3 w-24" />
			</div>
			<Skeleton className="h-9 w-20" />
		</div>
	);
}

export function HomeLastDownloadsSkeleton({
	className,
}: {
	className?: string;
}) {
	return (
		<div
			className={`rounded-xl ring-1 ring-foreground/10 bg-card p-4 flex flex-col gap-4 ${className ?? ""}`}
		>
			<Skeleton className="h-5 w-40" />
			<div className="flex flex-col gap-3">
				{Array.from({ length: 4 }).map((_, i) => (
					<div
						// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton
						key={i}
						className="flex items-center gap-3"
					>
						<Skeleton className="w-10 h-14 rounded shrink-0" />
						<div className="flex-1 flex flex-col gap-2">
							<Skeleton className="h-3 w-3/4" />
							<Skeleton className="h-3 w-1/2" />
						</div>
					</div>
				))}
			</div>
		</div>
	);
}

export function HomeTodayCalendarSkeleton({
	className,
}: {
	className?: string;
}) {
	return (
		<div
			className={`rounded-xl ring-1 ring-foreground/10 bg-card p-4 flex flex-col gap-4 ${className ?? ""}`}
		>
			<div className="flex items-center gap-2">
				<Skeleton className="size-4 rounded" />
				<Skeleton className="h-5 w-16" />
				<Skeleton className="h-5 w-16 rounded-full" />
			</div>
			<div className="grid grid-cols-2 gap-3">
				{Array.from({ length: 4 }).map((_, i) => (
					<Skeleton
						// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton
						key={i}
						className="aspect-[2/3] w-full rounded-md"
					/>
				))}
			</div>
		</div>
	);
}

export function HomeStorageSkeleton({ className }: { className?: string }) {
	return (
		<div
			className={`rounded-xl ring-1 ring-foreground/10 bg-card p-4 flex flex-col gap-4 ${className ?? ""}`}
		>
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-2">
					<Skeleton className="size-4 rounded" />
					<Skeleton className="h-5 w-16" />
				</div>
				<Skeleton className="h-7 w-20" />
			</div>
			<div className="flex flex-col gap-3">
				{Array.from({ length: 3 }).map((_, i) => (
					<div
						// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton
						key={i}
						className="flex flex-col gap-1.5"
					>
						<div className="flex items-center justify-between">
							<Skeleton className="h-3 w-2/3" />
							<Skeleton className="h-3 w-12" />
						</div>
						<Skeleton className="h-1.5 w-full rounded-full" />
					</div>
				))}
			</div>
		</div>
	);
}

export function HomeWelcomeSkeleton({ className }: { className?: string }) {
	return (
		<div
			className={`rounded-xl ring-1 ring-foreground/10 bg-card p-4 flex flex-col gap-4 ${className ?? ""}`}
		>
			<div className="flex items-start justify-between">
				<div className="flex flex-col gap-2">
					<Skeleton className="h-7 w-64" />
					<Skeleton className="h-4 w-48" />
				</div>
				<Skeleton className="hidden sm:block size-8" />
			</div>
			<Skeleton className="h-5 w-20 rounded-full" />
		</div>
	);
}

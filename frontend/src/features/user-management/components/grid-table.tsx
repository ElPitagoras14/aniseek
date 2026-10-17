import { ArrowDown, ArrowUp } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

// Same look as the Downloads list: a bordered, rounded container, a muted
// header row and grid rows that collapse into cards below `md`.
// `cols` must be a literal Tailwind class (e.g. "md:grid-cols-[1fr_120px]") so
// the compiler can see it.

export interface GridHeader {
	label: string;
	center?: boolean;
	// Makes the header a button that toggles the sort direction.
	sort?: { direction: "asc" | "desc"; onToggle: () => void };
}

interface GridTableProps {
	cols: string;
	headers: GridHeader[];
	minWidth?: string;
	children: ReactNode;
}

export function GridTable({
	cols,
	headers,
	minWidth = "md:min-w-[860px]",
	children,
}: GridTableProps) {
	return (
		<div className="overflow-hidden rounded-lg border">
			<div className="overflow-x-auto">
				<div className={minWidth}>
					<div
						className={cn(
							"hidden gap-4 border-b bg-muted/40 px-4 py-2 md:grid",
							cols,
						)}
					>
						{headers.map((header) => {
							const className = cn(
								"text-xs font-medium text-muted-foreground",
								header.center && "text-center",
							);
							if (!header.sort) {
								return (
									<span key={header.label || "actions"} className={className}>
										{header.label}
									</span>
								);
							}
							const SortIcon =
								header.sort.direction === "asc" ? ArrowUp : ArrowDown;
							return (
								<button
									key={header.label}
									type="button"
									onClick={header.sort.onToggle}
									className={cn(
										className,
										"flex items-center gap-1 transition-colors hover:text-foreground",
										header.center && "justify-center",
									)}
								>
									{header.label}
									<SortIcon className="size-3" />
								</button>
							);
						})}
					</div>
					{children}
				</div>
			</div>
		</div>
	);
}

export function GridRow({
	cols,
	children,
	className,
}: {
	cols: string;
	children: ReactNode;
	className?: string;
}) {
	return (
		<div
			className={cn(
				"flex flex-wrap items-center gap-x-3 gap-y-2 border-b px-3 py-3 last:border-b-0 md:grid md:gap-4 md:px-4 md:py-2.5",
				cols,
				className,
			)}
		>
			{children}
		</div>
	);
}

export function GridMessage({ children }: { children: ReactNode }) {
	return (
		<div className="px-4 py-8 text-center text-sm text-muted-foreground">
			{children}
		</div>
	);
}

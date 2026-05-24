import { LayoutGrid, ListTodo } from "lucide-react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

export type CalendarViewMode = "table" | "day";

interface CalendarViewToggleProps {
	value: CalendarViewMode;
	onChange: (mode: CalendarViewMode) => void;
}

export function CalendarViewToggle({
	value,
	onChange,
}: CalendarViewToggleProps) {
	return (
		<Tabs value={value} onValueChange={(v) => onChange(v as CalendarViewMode)}>
			<TabsList>
				<TabsTrigger value="table">
					<LayoutGrid />
					Table
				</TabsTrigger>
				<TabsTrigger value="day">
					<ListTodo />
					Day
				</TabsTrigger>
			</TabsList>
		</Tabs>
	);
}

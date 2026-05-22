import { Search } from "lucide-react";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Input } from "@/components/ui/input";

interface DownloadsSearchInputProps {
	defaultValue?: string;
	onDebouncedChange: (value: string) => void;
}

export function DownloadsSearchInput({
	defaultValue = "",
	onDebouncedChange,
}: DownloadsSearchInputProps) {
	const [value, setValue] = useState(defaultValue);
	const callbackRef = useRef(onDebouncedChange);
	const isFirstRender = useRef(true);

	useLayoutEffect(() => {
		callbackRef.current = onDebouncedChange;
	});

	useEffect(() => {
		if (isFirstRender.current) {
			isFirstRender.current = false;
			return;
		}
		setValue(defaultValue);
	}, [defaultValue]);

	useEffect(() => {
		const timer = setTimeout(() => {
			callbackRef.current(value);
		}, 300);
		return () => clearTimeout(timer);
	}, [value]);

	return (
		<div className="relative w-full max-w-xl">
			<Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
			<Input
				value={value}
				onChange={(e) => setValue(e.target.value)}
				placeholder="Buscar por nombre del anime…"
				className="pl-9"
			/>
		</div>
	);
}

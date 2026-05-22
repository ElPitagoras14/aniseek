import { Search } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface SearchFormProps {
	defaultValue?: string;
	onSubmit: (query: string) => void;
}

export function SearchForm({ defaultValue = "", onSubmit }: SearchFormProps) {
	const [value, setValue] = useState(defaultValue);

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		const trimmed = value.trim();
		if (trimmed) onSubmit(trimmed);
	};

	return (
		<form onSubmit={handleSubmit} className="flex gap-2 w-full max-w-xl">
			<Input
				value={value}
				onChange={(e) => setValue(e.target.value)}
				placeholder="Enter a search term..."
				className="flex-1"
			/>
			<Button type="submit">
				<Search className="size-4 mr-2" />
				Search
			</Button>
		</form>
	);
}

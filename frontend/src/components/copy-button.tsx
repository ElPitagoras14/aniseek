import { Check, Copy } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { copyText } from "@/lib/clipboard";

export function CopyButton({
	text,
	label,
	disabled,
}: {
	text: string;
	label: string;
	disabled?: boolean;
}) {
	const [copied, setCopied] = useState(false);

	const copy = async () => {
		try {
			await copyText(text);
			setCopied(true);
			setTimeout(() => setCopied(false), 2000);
		} catch {
			toast.error("Could not copy. Select the text and copy it manually.");
		}
	};

	return (
		<Button
			type="button"
			variant="outline"
			size="icon"
			onClick={copy}
			disabled={disabled}
			aria-label={label}
			className="shrink-0"
		>
			{copied ? <Check /> : <Copy />}
		</Button>
	);
}

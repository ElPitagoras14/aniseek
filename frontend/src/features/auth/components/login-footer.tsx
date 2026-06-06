import { SiBuymeacoffee, SiGithub } from "@icons-pack/react-simple-icons";
import { Separator } from "@/components/ui/separator";

export function LoginFooter() {
	return (
		<div className="flex items-center justify-center gap-3 text-sm text-muted-foreground">
			<a
				href="https://github.com/ElPitagoras14/aniseek"
				target="_blank"
				rel="noreferrer"
				className="flex items-center gap-2"
			>
				<SiGithub className="size-4" />
				Github
			</a>
			<Separator orientation="vertical" className="h-4" />
			<a
				href="https://buymeacoffee.com/jhonyg"
				target="_blank"
				rel="noreferrer"
				className="flex items-center gap-2"
			>
				<SiBuymeacoffee className="size-4" />
				Support it
			</a>
		</div>
	);
}

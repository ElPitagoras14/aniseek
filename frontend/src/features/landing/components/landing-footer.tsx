import { Separator } from "@/components/ui/separator";
import { LandingLogo } from "./landing-logo";

export function LandingFooter() {
	return (
		<footer className="border-t">
			<div className="mx-auto w-full max-w-6xl px-4 py-8 md:px-6 lg:px-8">
				<div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
					<div className="flex items-center gap-3">
						<LandingLogo />
						<Separator orientation="vertical" className="h-4" />
						<span className="font-mono text-xs text-muted-foreground">
							v{__APP_VERSION__}
						</span>
					</div>
					<div className="flex flex-col items-center gap-1 sm:items-end">
						<p className="text-xs text-muted-foreground">&copy; 2026 AniSeek</p>
						<p className="text-xs text-muted-foreground">
							Created with ❤️ by{" "}
							<a
								href="https://github.com/ElPitagoras14"
								target="_blank"
								rel="noreferrer"
								className="font-medium text-foreground hover:underline underline-offset-4"
							>
								ElPitagoras14
							</a>
						</p>
					</div>
				</div>
			</div>
		</footer>
	);
}

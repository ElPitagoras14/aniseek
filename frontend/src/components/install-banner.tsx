import { Download, X } from "lucide-react";
import { Button } from "#/components/ui/button";
import { usePWAInstall } from "#/hooks/use-pwa-install";

export function InstallBanner() {
	const { isInstallable, install, dismiss } = usePWAInstall();

	if (!isInstallable) return null;

	return (
		<div className="fixed bottom-0 left-0 right-0 z-50 p-4 animate-in slide-in-from-bottom duration-300">
			<div className="flex items-center justify-between gap-4 rounded-xl border border-border bg-card px-4 py-3 shadow-lg max-w-lg mx-auto">
				<div className="flex items-center gap-3">
					<img
						src="/logo192.png"
						alt="AniSeek"
						className="h-10 w-10 rounded-lg shrink-0"
					/>
					<div>
						<p className="text-sm font-semibold">Instala AniSeek como app</p>
						<p className="text-xs text-muted-foreground">
							Accede más rápido desde tu pantalla de inicio
						</p>
					</div>
				</div>
				<div className="flex items-center gap-2 shrink-0">
					<Button
						variant="ghost"
						size="icon"
						onClick={dismiss}
						aria-label="Descartar"
					>
						<X className="h-4 w-4" />
					</Button>
					<Button size="sm" onClick={install}>
						<Download className="mr-1.5 h-4 w-4" />
						Instalar
					</Button>
				</div>
			</div>
		</div>
	);
}

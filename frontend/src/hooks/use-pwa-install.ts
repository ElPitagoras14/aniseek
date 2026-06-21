import { useEffect, useState } from "react";

interface BeforeInstallPromptEvent extends Event {
	prompt(): Promise<void>;
	userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

declare global {
	interface WindowEventMap {
		beforeinstallprompt: BeforeInstallPromptEvent;
	}
}

const DISMISSED_KEY = "pwa-install-dismissed";

export function usePWAInstall() {
	const [deferredPrompt, setDeferredPrompt] =
		useState<BeforeInstallPromptEvent | null>(null);
	const [isInstallable, setIsInstallable] = useState(false);

	useEffect(() => {
		if (localStorage.getItem(DISMISSED_KEY)) return;

		const handler = (e: BeforeInstallPromptEvent) => {
			e.preventDefault();
			setDeferredPrompt(e);
			setIsInstallable(true);
		};

		window.addEventListener("beforeinstallprompt", handler);
		return () => window.removeEventListener("beforeinstallprompt", handler);
	}, []);

	const install = async () => {
		if (!deferredPrompt) return;
		deferredPrompt.prompt();
		await deferredPrompt.userChoice;
		setDeferredPrompt(null);
		setIsInstallable(false);
	};

	const dismiss = () => {
		localStorage.setItem(DISMISSED_KEY, "true");
		setIsInstallable(false);
	};

	return { isInstallable, install, dismiss };
}

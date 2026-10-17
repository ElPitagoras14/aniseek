// Copies text to the clipboard. The async Clipboard API only exists in secure
// contexts (HTTPS or localhost), so an instance opened over plain HTTP on the
// LAN (http://192.168.x.x) falls back to the legacy execCommand path.
export async function copyText(text: string): Promise<void> {
	if (navigator.clipboard && window.isSecureContext) {
		await navigator.clipboard.writeText(text);
		return;
	}

	const textarea = document.createElement("textarea");
	textarea.value = text;
	textarea.setAttribute("readonly", "");
	textarea.style.position = "fixed";
	textarea.style.top = "0";
	textarea.style.left = "0";
	textarea.style.opacity = "0";
	// Inside an open dialog, its focus trap would pull focus back from an
	// element appended to <body> and the copy would select nothing.
	const container =
		document.activeElement?.closest('[role="dialog"]') ?? document.body;
	container.appendChild(textarea);

	const previous = document.activeElement as HTMLElement | null;
	textarea.focus();
	textarea.select();
	try {
		if (!document.execCommand("copy")) {
			throw new Error("Copy command was rejected");
		}
	} finally {
		container.removeChild(textarea);
		previous?.focus();
	}
}

export function formatBytes(bytes: number | null | undefined): string {
	if (bytes == null || bytes === 0) return "0 B";
	const units = ["B", "KB", "MB", "GB", "TB"];
	const i = Math.floor(Math.log(bytes) / Math.log(1024));
	const value = bytes / 1024 ** i;
	return `${value.toFixed(value < 10 && i > 0 ? 1 : 0)} ${units[i]}`;
}

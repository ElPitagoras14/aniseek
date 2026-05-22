export function parseEpisodeRange(
	input: string,
	max: number,
): { episodes: number[]; error: string | null } {
	const trimmed = input.trim();
	if (!trimmed) return { episodes: [], error: "Ingresa al menos un episodio." };

	const parts = trimmed
		.split(",")
		.map((p) => p.trim())
		.filter(Boolean);
	const set = new Set<number>();

	for (const part of parts) {
		if (part.includes("-")) {
			const dashes = (part.match(/-/g) ?? []).length;
			if (dashes !== 1) {
				return { episodes: [], error: `Rango inválido: "${part}".` };
			}
			const [startStr, endStr] = part.split("-");
			const start = Number(startStr);
			const end = Number(endStr);
			if (!Number.isInteger(start) || !Number.isInteger(end)) {
				return { episodes: [], error: `Rango inválido: "${part}".` };
			}
			if (start > end) {
				return { episodes: [], error: `El rango "${part}" está invertido.` };
			}
			if (start < 1 || end > max) {
				return {
					episodes: [],
					error: `Los episodios deben estar entre 1 y ${max}.`,
				};
			}
			for (let i = start; i <= end; i++) set.add(i);
		} else {
			const n = Number(part);
			if (!Number.isInteger(n) || Number.isNaN(n)) {
				return { episodes: [], error: `Episodio inválido: "${part}".` };
			}
			if (n < 1 || n > max) {
				return {
					episodes: [],
					error: `El episodio ${n} está fuera de rango (1-${max}).`,
				};
			}
			set.add(n);
		}
	}

	return { episodes: Array.from(set).sort((a, b) => a - b), error: null };
}

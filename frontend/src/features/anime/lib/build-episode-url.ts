export function buildEpisodeUrl(
	platform: string,
	animeId: string,
	episodeNumber: number,
): string | null {
	if (platform === "AnimeAV1") {
		return `https://animeav1.com/media/${animeId}/${episodeNumber}`;
	}
	return null;
}

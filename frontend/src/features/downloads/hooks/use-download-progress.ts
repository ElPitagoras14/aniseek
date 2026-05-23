import { useEffect, useState } from "react";
import type { DownloadStatus } from "../types";

interface ProgressMeta {
	size?: number;
	progress?: number;
	retry_count?: number;
	max_retries?: number;
}

export interface DownloadProgress {
	state: DownloadStatus;
	meta: ProgressMeta;
}

export function useDownloadProgress(
	jobIds: string[],
): Record<string, DownloadProgress> {
	const [progress, setProgress] = useState<Record<string, DownloadProgress>>(
		{},
	);

	// biome-ignore lint/correctness/useExhaustiveDependencies: computed string dep avoids array reference comparisons
	useEffect(() => {
		const csv = jobIds.join(",");
		if (!csv) {
			setProgress({});
			return;
		}

		const params = new URLSearchParams({ job_ids: csv });
		const es = new EventSource(`/api/episodes/stream/status?${params}`);

		es.onerror = () => {
			es.close();
		};

		es.onmessage = (event) => {
			try {
				const payload = JSON.parse(event.data) as {
					job_id: string;
					state: DownloadStatus;
					meta: ProgressMeta;
				};
				setProgress((prev) => ({
					...prev,
					[payload.job_id]: { state: payload.state, meta: payload.meta },
				}));
			} catch {
				// ignore malformed events
			}
		};

		return () => {
			es.close();
		};
	}, [jobIds.join(",")]);

	return progress;
}

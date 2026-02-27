// contexts/download-progress-context.tsx
"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

interface ProgressMeta {
  jobId: string;
  state: string;
  progress?: number;
  size?: number;
}

interface DownloadProgressContextValue {
  progressMap: Record<string, ProgressMeta>;
  setJobIds: (ids: string[]) => void;
}

const DownloadProgressContext =
  createContext<DownloadProgressContextValue | null>(null);

export const useDownloadProgress = () => {
  const ctx = useContext(DownloadProgressContext);
  if (!ctx)
    throw new Error(
      "useDownloadProgress must be used inside DownloadProgressProvider"
    );
  return ctx;
};

export const DownloadProgressProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [progressMap, setProgressMap] = useState<Record<string, ProgressMeta>>(
    {}
  );
  const [jobIds, setJobIds] = useState<string[]>([]);
  const sourceRef = useRef<EventSource | null>(null);

  const sseBaseURL =
    process.env.NODE_ENV === "development"
      ? "http://localhost:4000/sse"
      : "/sse";

  useEffect(() => {
    if (jobIds.length === 0) return;

    if (sourceRef.current) {
      sourceRef.current.close();
    }

    const source = new EventSource(
      `${sseBaseURL}/animes/stream/download?job_ids=${jobIds.join(",")}`
    );
    sourceRef.current = source;

    source.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { job_id, state, meta } = data;

        setProgressMap((prev) => ({
          ...prev,
          [job_id]: {
            jobId: job_id,
            state,
            progress: meta?.progress,
            size: meta?.total,
          },
        }));
      } catch (err) {
        console.error("Error parsing SSE:", err);
      }
    };

    source.onerror = (err) => {
      console.error("SSE Error:", err);
      source.close();
    };

    return () => {
      source.close();
    };
  }, [jobIds]);

  return (
    <DownloadProgressContext.Provider value={{ progressMap, setJobIds }}>
      {children}
    </DownloadProgressContext.Provider>
  );
};

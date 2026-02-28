"use client";

import { useEffect, useState, useRef } from "react";
import { useDownloadProgress } from "@/providers/progress-provider";

interface ProgressMeta {
  jobId: string;
  state: string;
  progress?: number;
  size?: number;
}

export const useJobProgress = (jobId: string | null) => {
  const { progressMap } = useDownloadProgress();
  const [progress, setProgress] = useState<ProgressMeta | null>(null);
  const prevJobIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setProgress(null);
      prevJobIdRef.current = null;
      return;
    }

    const currentProgress = progressMap[jobId];
    const prevJobId = prevJobIdRef.current;

    if (jobId !== prevJobId || currentProgress !== progress) {
      setProgress(currentProgress);
      prevJobIdRef.current = jobId;
    }
  }, [progressMap, jobId, progress]);

  return progress;
};

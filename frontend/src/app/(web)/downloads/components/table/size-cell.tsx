"use client";

import { formatSize } from "@/lib/utils";
import { useJobProgress } from "@/hooks/use-job-progress";
import { memo } from "react";

interface SizeCellProps {
  size: number | null;
  jobId: string | null;
}

export const SizeCell = memo(({ size, jobId }: SizeCellProps) => {
  const jobProgress = useJobProgress(jobId);

  const effectiveSize = jobProgress?.size || size;

  return <div className="text-center">{formatSize(effectiveSize)}</div>;
});

SizeCell.displayName = "SizeCell";

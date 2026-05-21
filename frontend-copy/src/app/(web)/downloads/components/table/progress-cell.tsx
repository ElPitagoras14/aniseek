"use client";

import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { DownloadIcon } from "lucide-react";
import { useJobProgress } from "@/hooks/use-job-progress";
import { memo } from "react";

const apiBaseURL =
  process.env.NODE_ENV === "development"
    ? "http://localhost:4000"
    : "";

interface ProgressCellProps {
  status: string;
  progress: number;
  id: number;
  jobId: string | null;
  role: string;
}

export const ProgressCell = memo(
  ({ status, progress, id, jobId, role }: ProgressCellProps) => {
    const jobProgress = useJobProgress(jobId);

    const effectiveStatus = jobProgress?.state || status;
    const effectiveProgress = jobProgress?.progress || progress;

    if (effectiveStatus === "DOWNLOADING" && effectiveProgress) {
      return (
        <div className="flex justify-center items-center">
          <div className="w-60 flex justify-center items-center gap-x-2">
            <Progress value={effectiveProgress} className="w-60" />
            <span>{parseFloat(effectiveProgress.toFixed(2))}%</span>
          </div>
        </div>
      );
    }

    if (effectiveStatus === "SUCCESS") {
      return (
        <div className="flex flex-col justify-center items-center">
          <div className="max-w-70" />
          <Button
            variant="ghost"
            size="icon"
            disabled={role !== "admin" && role !== "member"}
            onClick={() =>
              (window.location.href = `${apiBaseURL}/api/v1/animes/download/episode/${id}`)
            }
            className="cursor-pointer"
          >
            <DownloadIcon />
          </Button>
        </div>
      );
    }

    return (
      <div className="flex justify-center">
        <div className="text-center w-70">{effectiveStatus}</div>
      </div>
    );
  }
);

ProgressCell.displayName = "ProgressCell";

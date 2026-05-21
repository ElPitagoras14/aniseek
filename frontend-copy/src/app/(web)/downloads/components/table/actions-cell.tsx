import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Spinner } from "@/components/ui/spinner";
import { EpisodeDownload } from "@/lib/interfaces";
import { EllipsisIcon } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

interface ActionsCellProps {
  row: EpisodeDownload;
  role: string;
  handleForceDownload: (
    animeId: string,
    episodeNumber: number
  ) => Promise<void>;
  handleDeleteDownload: (
    animeId: string,
    episodeNumber: number
  ) => Promise<void>;
}

export default function ActionsCell({
  row,
  role,
  handleForceDownload,
  handleDeleteDownload,
}: ActionsCellProps) {
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  const handleForceDownloadClick = async () => {
    setIsDownloading(true);
    await handleForceDownload(row.animeId, row.episodeNumber);
    setIsDownloading(false);
  };

  const handleDeleteDownloadClick = async () => {
    setIsDeleting(true);
    await handleDeleteDownload(row.animeId, row.episodeNumber);
    setIsDeleting(false);
  };

  return (
    <div className="flex justify-center">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="cursor-pointer">
            <EllipsisIcon />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem asChild>
            <Link
              href={`/anime/${row.animeId}`}
              className="w-full cursor-pointer"
            >
              Go to anime
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem
            className="cursor-pointer"
            disabled={!role || role === "guest"}
            onClick={handleForceDownloadClick}
          >
            Force re download {isDownloading && <Spinner />}
          </DropdownMenuItem>
          <DropdownMenuItem
            className="cursor-pointer"
            disabled={!role || role === "guest"}
            onClick={handleDeleteDownloadClick}
          >
            Delete download {isDeleting && <Spinner />}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}

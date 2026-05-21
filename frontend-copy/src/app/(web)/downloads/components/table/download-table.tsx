import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { EpisodeDownload } from "@/lib/interfaces";
import { cn, formatSize } from "@/lib/utils";
import Link from "next/link";
import Image from "next/image";
import { ProgressCell } from "./progress-cell";
import ActionsCell from "./actions-cell";
import { Skeleton } from "@/components/ui/skeleton";
import { Pagination } from "./pagination";
import { PaginationState } from "@tanstack/react-table";
import { AspectRatio } from "@/components/ui/aspect-ratio";

interface DownloadTableProps {
  data: EpisodeDownload[];
  role: string;
  isLoading: boolean;
  handleForceDownload: (
    animeId: string,
    episodeNumber: number
  ) => Promise<void>;
  handleDeleteDownload: (
    animeId: string,
    episodeNumber: number
  ) => Promise<void>;
  serverInfo: {
    total: number;
    pagination: PaginationState;
    setPagination: (pagination: PaginationState) => void;
  };
  containerClassName?: string;
  tableClassName?: string;
}

export function DownloadTable({
  data,
  role = "guest",
  isLoading,
  handleForceDownload,
  handleDeleteDownload,
  serverInfo,
  containerClassName,
  tableClassName,
}: DownloadTableProps) {
  return (
    <div className={cn("flex flex-col gap-y-4", containerClassName)}>
      <div className={cn("overflow-hidden rounded-md border", tableClassName)}>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="text-center">Poster</TableHead>
              <TableHead>Title</TableHead>
              <TableHead className="text-center">Episode</TableHead>
              <TableHead className="text-center">Status</TableHead>
              <TableHead className="text-center">Size</TableHead>
              <TableHead className="text-center">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6}>
                  <Skeleton className="h-10 w-full" />
                </TableCell>
              </TableRow>
            ) : (
              data?.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>
                    <div className="flex justify-center max-w-32 mx-auto">
                      <AspectRatio ratio={3 / 4}>
                        <Link href={`/anime/${row.animeId}`}>
                          <Image
                            src={row.poster}
                            alt={row.title}
                            fill
                            className="rounded-md object-cover"
                          />
                        </Link>
                      </AspectRatio>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm md:text-base">
                    {row.title}
                  </TableCell>
                  <TableCell className="text-center">
                    {row.episodeNumber}
                  </TableCell>
                  <TableCell>
                    <ProgressCell
                      status={row.status}
                      progress={row.progress}
                      id={row.id}
                      jobId={row.jobId}
                      role={role}
                    />
                  </TableCell>
                  <TableCell className="text-center">
                    {formatSize(row.size)}
                  </TableCell>
                  <TableCell>
                    <ActionsCell
                      row={row}
                      role={role}
                      handleForceDownload={handleForceDownload}
                      handleDeleteDownload={handleDeleteDownload}
                    />
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex justify-end">
        <Pagination
          pagination={serverInfo.pagination}
          setPagination={serverInfo.setPagination}
          total={serverInfo.total}
        />
      </div>
    </div>
  );
}

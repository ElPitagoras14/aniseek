"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useEffect, useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { CheckIcon, ChevronsUpDownIcon } from "lucide-react";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { cn } from "@/lib/utils";
import { PaginationState, SortingState } from "@tanstack/react-table";
import { useSession } from "next-auth/react";
import { toast } from "sonner";
import { useDownloadProgress } from "@/providers/progress-provider";
import { EpisodeDownload } from "@/lib/interfaces";
import { DownloadTable } from "./components/table/download-table";

interface QueryParams {
  sorting?: {
    id: string;
    desc: boolean;
  }[];
  pagination?: {
    pageIndex: number;
    pageSize: number;
  };
}

interface DownloadParams {
  limit: number;
  page: number;
  anime_id?: string;
}

const getDownloads = (animeId: string, queryParams: QueryParams) => {
  const { pagination: { pageIndex = 0, pageSize = 10 } = {} } = queryParams;

  const params: DownloadParams = {
    limit: pageSize,
    page: pageIndex + 1,
  };

  const options = {
    method: "GET",
    url: "/animes/download",
    params,
  };

  if (animeId) {
    options.params.anime_id = animeId;
  }

  return apiClient(options);
};

const getUniqueAnimes = () => {
  const options = {
    method: "GET",
    url: "/animes/download/anime",
  };
  return apiClient(options);
};

interface ForceDownloadParams {
  animeId: string;
  episodeNumber: number;
}

const forceDownload = ({ animeId, episodeNumber }: ForceDownloadParams) => {
  const options = {
    method: "POST",
    url: `/animes/download/single/${animeId}/${episodeNumber}`,
    params: {
      force_download: true,
    },
  };
  return apiClient(options);
};

interface DeleteDownloadParams {
  animeId: string;
  episodeNumber: number;
}

const deleteDownload = ({ animeId, episodeNumber }: DeleteDownloadParams) => {
  const options = {
    method: "DELETE",
    url: `/animes/download/single/${animeId}/${episodeNumber}`,
  };
  return apiClient(options);
};

interface Anime {
  id: string;
  title: string;
}

export default function Downloads() {
  const [open, setOpen] = useState<boolean>(false);
  const [animeId, setAnimeId] = useState<string>("");
  const [sorting] = useState<SortingState>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const { data: session } = useSession();
  const { user } = session || {};
  const { setJobIds } = useDownloadProgress();

  const queryParams = {
    pagination,
    sorting,
  };

  const { data: animesData } = useQuery({
    queryKey: ["animes"],
    queryFn: getUniqueAnimes,
    refetchOnWindowFocus: false,
  });

  const {
    data: serverData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["downloads", animeId, queryParams],
    queryFn: () => getDownloads(animeId, queryParams),
    refetchOnWindowFocus: false,
  });

  const animes = animesData?.data?.payload?.items;

  const forceDownloadMutation = useMutation({
    mutationFn: forceDownload,
    onSuccess: async () => {
      await refetch();
    },
  });

  const handleForceDownload = async (
    animeId: string,
    episodeNumber: number
  ) => {
    forceDownloadMutation.mutate({
      animeId,
      episodeNumber,
    });
  };

  const deleteDownloadMutation = useMutation({
    mutationFn: deleteDownload,
    onSuccess: async (_, values) => {
      await refetch();
      toast.success(
        `Episode ${values.animeId} - ${values.episodeNumber} deleted`
      );
    },
  });

  const handleDeleteDownload = async (
    animeId: string,
    episodeNumber: number
  ) => {
    deleteDownloadMutation.mutate({
      animeId,
      episodeNumber,
    });
  };

  useEffect(() => {
    if (!serverData) return;

    const items = serverData?.data?.payload?.items;

    const jobIds = items
      .filter(
        (episode: EpisodeDownload) =>
          episode.jobId &&
          episode.status !== "SUCCESS" &&
          episode.status !== "FAILED"
      )
      .map((episode: EpisodeDownload) => episode.jobId as string);

    setJobIds(jobIds);
  }, [serverData, setJobIds]);

  return (
    <div className="flex flex-col gap-y-4">
      <div className="flex flex-row lg:flex-col gap-y-4 justify-between items-center lg:items-start">
        <span className="text-xl md:text-2xl lg:text-3xl font-semibold">
          Downloads
        </span>
        <div className="">
          <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                role="combobox"
                aria-expanded={open}
                className="min-w-48 justify-between"
              >
                {animeId
                  ? animes.find((anime: Anime) => anime.id === animeId)?.title
                  : "All"}
                <ChevronsUpDownIcon className="ml-2 h-4 w-4 shrink-0 opacity-50" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-48 p-0">
              <Command>
                <CommandInput placeholder="Select an anime" />
                <CommandList>
                  <CommandEmpty>No downloads found</CommandEmpty>
                  <CommandGroup>
                    {animes?.map((anime: Anime) => (
                      <CommandItem
                        key={anime.id}
                        value={anime.id}
                        onSelect={(currentValue) => {
                          setAnimeId(
                            currentValue === animeId ? "" : currentValue
                          );
                          setOpen(false);
                        }}
                        className="flex items-center justify-between"
                      >
                        {anime.title}
                        <CheckIcon
                          className={cn(
                            "ml-auto",
                            animeId === anime.id ? "opacity-100" : "opacity-0"
                          )}
                        />
                      </CommandItem>
                    ))}
                  </CommandGroup>
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>
        </div>
      </div>
      <DownloadTable
        data={serverData?.data?.payload?.items || []}
        role={user?.role || "guest"}
        isLoading={isLoading}
        handleForceDownload={handleForceDownload}
        handleDeleteDownload={handleDeleteDownload}
        serverInfo={{
          total: serverData?.data?.payload?.total || 0,
          pagination,
          setPagination,
        }}
      />
    </div>
  );
}

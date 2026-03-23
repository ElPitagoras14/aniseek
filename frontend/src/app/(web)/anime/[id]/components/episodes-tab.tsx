"use client";

import { AnimeInfo } from "../page";
import { Button } from "@/components/ui/button";
import {
  ArrowDownNarrowWideIcon,
  ArrowUpNarrowWideIcon,
  CircleCheckIcon,
  CircleXIcon,
  DownloadIcon,
  PlayIcon,
} from "lucide-react";
import { useRef, useState } from "react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { z } from "zod";
import { FormField } from "@/lib/interfaces";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import CustomField from "@/components/form-fields/custom-field";
import { Form } from "@/components/ui/form";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useMutation } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { toast } from "sonner";
import { AxiosError } from "axios";

const episodesPattern = /^(\d+(-\d+)?)(,(\d+(-\d+)?))*$/;
const estimatedSize = 50;

const fields: FormField[] = [
  {
    name: "downloadRange",
    placeholder: "1-4,7,8-10,12",
    type: "text",
    validation: z
      .string()
      .optional()
      .refine(
        (text = "") => {
          if (!text.trim()) return true; // vacío → válido
          return episodesPattern.test(text);
        },
        {
          message: "Formato inválido. Ejemplo: 1-4,7,8-10,12",
        },
      ),
  },
];

const formSchema = z.object(
  fields.reduce(
    (acc, field) => {
      acc[field.name] = field.validation;
      return acc;
    },
    {} as Record<string, z.ZodType>,
  ),
);

interface DownloadEpisode {
  episodeId: number;
  animeId: string;
}

const downloadAnime = ({ episodeId, animeId }: DownloadEpisode) => {
  const options = {
    method: "POST",
    url: `/animes/download/single/${animeId}/${episodeId}`,
  };

  return apiClient(options);
};

interface DownloadBulkEpisode {
  episodeIds: number[];
  animeId: string;
}

const downloadBulkAnime = ({ episodeIds, animeId }: DownloadBulkEpisode) => {
  const options = {
    method: "POST",
    url: `/animes/download/bulk/${animeId}`,
    data: episodeIds,
  };

  return apiClient(options);
};

const getIdx = (idx: number, order: "asc" | "desc", total: number) => {
  if (order === "asc") {
    return idx + 1;
  } else {
    return total - idx;
  }
};

interface BulkEpisode {
  episode_number: number;
  success: boolean;
}

interface EpisodesTabProps {
  anime: AnimeInfo;
}

export default function EpisodesTab({ anime }: EpisodesTabProps) {
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const downloadMutation = useMutation({
    mutationFn: downloadAnime,
    onSuccess: (_, values) => {
      toast.success(`Episode ${values.episodeId} enqueued`);
    },
    onError: (error: AxiosError) => {
      let message = error.message;

      if (error.isAxiosError) {
        const axiosError = error as AxiosError<{ message: string }>;
        message = axiosError.response?.data?.message || axiosError.message;
      } else if (error instanceof Error) {
        message = error.message;
      }

      toast.error(message);
    },
  });

  const downloadBulkMutation = useMutation({
    mutationFn: downloadBulkAnime,
    onSuccess: (response) => {
      const {
        data: {
          payload: { items },
        },
      } = response;
      const failed = items.filter((item: BulkEpisode) => !item.success);
      const success = items.filter((item: BulkEpisode) => item.success);
      if (failed.length === 0) {
        toast.success(`All episodes enqueued`);
      }
      if (failed.length > 0) {
        toast.error(
          `Episodes enqueued: ${success.length}. Failed ${failed
            .map((item: BulkEpisode) => item.episode_number)
            .join(",")} episodes`,
        );
      }
    },
    onError: (error: AxiosError) => {
      let message = error.message;

      if (error.isAxiosError) {
        const axiosError = error as AxiosError<{ message: string }>;
        message = axiosError.response?.data?.message || axiosError.message;
      } else if (error instanceof Error) {
        message = error.message;
      }

      toast.error(message);
    },
  });

  const parentRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: anime.episodes.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => estimatedSize,
    overscan: 25,
  });

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      downloadRange: "",
    },
  });

  const downloadRangeValue = form.watch("downloadRange");
  const isDownloadDisabled =
    !downloadRangeValue || downloadBulkMutation.isPending;

  const baseUrl = `https://animeav1.com/media/${anime.id}`;

  const sortedEpisodes = anime.episodes.sort((a, b) => {
    const idA = a.id;
    const idB = b.id;

    if (sortOrder === "asc") {
      return idA - idB;
    } else {
      return idB - idA;
    }
  });

  const onSubmit = form.handleSubmit(
    async (values: z.infer<typeof formSchema>) => {
      const text = values.downloadRange as string;

      if (!text) return;

      const episodes: number[] = text
        .split(",")
        .flatMap((part) => {
          if (!part) return [];
          if (part.includes("-")) {
            const [start, end] = part.split("-").map(Number);
            return Array.from({ length: end - start + 1 }, (_, i) => start + i);
          }
          return [Number(part)];
        })
        .filter(Boolean);
      downloadBulkMutation.mutate({
        animeId: anime.id,
        episodeIds: episodes,
      });
    },
  );

  return (
    <div className="flex flex-col gap-y-3">
      <Form {...form}>
        <form className="flex flex-row gap-x-4 mt-2 items-center">
          <div className="w-full">
            {fields.map((field) => (
              <CustomField
                key={field.name}
                form={form}
                fieldInfo={field}
                inputClassName="h-10"
              />
            ))}
          </div>
          {sortOrder === "asc" ? (
            <Tooltip>
              <TooltipTrigger type="button">
                <ArrowUpNarrowWideIcon
                  className="w-6 h-6 cursor-pointer hover:text-indigo-500"
                  onClick={() => setSortOrder("desc")}
                />
              </TooltipTrigger>
              <TooltipContent>Sort in descending order</TooltipContent>
            </Tooltip>
          ) : (
            <Tooltip>
              <TooltipTrigger type="button">
                <ArrowDownNarrowWideIcon
                  className="w-6 h-6 cursor-pointer hover:text-indigo-500"
                  onClick={() => setSortOrder("asc")}
                />
              </TooltipTrigger>
              <TooltipContent>Sort in ascending order</TooltipContent>
            </Tooltip>
          )}
          <Button
            disabled={isDownloadDisabled}
            onClick={onSubmit}
            type="button"
            className="cursor-pointer"
          >
            Download
          </Button>
        </form>
      </Form>
      <div className="border rounded-md">
        <div className="grid grid-cols-4 gap-2 items-center px-4 py-3 border-b hover:bg-muted/50">
          <div>Id</div>
          <div>Episode</div>
          <div className="text-center">Downloaded</div>
          <div className="text-center">Actions</div>
        </div>
        <div
          ref={parentRef}
          className="overflow-y-auto relative custom-scrollbar max-h-[500px]"
        >
          <div
            style={{
              height: rowVirtualizer.getTotalSize(),
              position: "relative",
            }}
          >
            {rowVirtualizer.getVirtualItems().map((virtualRow) => {
              const episode = sortedEpisodes[virtualRow.index];
              const idx = virtualRow.index;

              return (
                <div
                  key={episode.id}
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    height: virtualRow.size,
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                  className="grid grid-cols-4 gap-2 items-center px-4 py-3 border-b hover:bg-muted/50"
                >
                  <div>{getIdx(idx, sortOrder, anime.episodes.length)}</div>
                  <div>Episode {episode.id}</div>
                  <div className="flex justify-center items-center">
                    {episode.isUserDownloaded ? (
                      <Tooltip>
                        <TooltipTrigger>
                          <CircleCheckIcon className="text-green-500 dark:text-green-400" />
                        </TooltipTrigger>
                        <TooltipContent>Downloaded by you</TooltipContent>
                      </Tooltip>
                    ) : episode.isGlobalDownloaded ? (
                      <Tooltip>
                        <TooltipTrigger>
                          <CircleCheckIcon className="text-indigo-500 dark:text-indigo-400" />
                        </TooltipTrigger>
                        <TooltipContent>
                          Downloaded by other user
                        </TooltipContent>
                      </Tooltip>
                    ) : (
                      <Tooltip>
                        <TooltipTrigger>
                          <CircleXIcon className="text-red-500 dark:text-red-400" />
                        </TooltipTrigger>
                        <TooltipContent>Not downloaded yet</TooltipContent>
                      </Tooltip>
                    )}
                  </div>
                  <div className="flex justify-center gap-2">
                    <Tooltip>
                      <TooltipTrigger>
                        <PlayIcon
                          className="w-6 h-6 cursor-pointer hover:text-indigo-500"
                          onClick={() =>
                            window.open(`${baseUrl}/${episode.id}`, "_blank")
                          }
                        />
                      </TooltipTrigger>
                      <TooltipContent>Go to website</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                      <TooltipTrigger>
                        <DownloadIcon
                          className="w-6 h-6 cursor-pointer hover:text-indigo-500"
                          onClick={() =>
                            downloadMutation.mutate({
                              animeId: anime.id,
                              episodeId: episode.id,
                            })
                          }
                        />
                      </TooltipTrigger>
                      <TooltipContent>Download episode</TooltipContent>
                    </Tooltip>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

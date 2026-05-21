"use client";

import { Badge } from "@/components/ui/badge";
import { AnimeInfo } from "../page";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { BookmarkIcon } from "lucide-react";
import Image from "next/image";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { toast } from "sonner";
import { AxiosError } from "axios";
import { AspectRatio } from "@/components/ui/aspect-ratio";

const saveAnime = (animeId: string) => {
  const options = {
    method: "PUT",
    url: `/animes/save/${animeId}`,
  };

  return apiClient(options);
};

const unsaveAnime = (animeId: string) => {
  const options = {
    method: "PUT",
    url: `/animes/unsave/${animeId}`,
  };

  return apiClient(options);
};

interface SidebarInfoProps {
  anime: AnimeInfo;
}

export default function SidebarInfo({ anime }: SidebarInfoProps) {
  const [isSaved, setIsSaved] = useState<boolean>(anime.isSaved);

  const saveMutation = useMutation({
    mutationFn: saveAnime,
    onSuccess: () => {
      toast.success(`${anime.title} saved`);
    },
    onError: (error: AxiosError) => {
      let message = error.message;

      if (error.isAxiosError) {
        const axiosError = error as AxiosError<{ message: string }>;
        message = axiosError.response?.data?.message || axiosError.message;
      } else if (error instanceof Error) {
        message = error.message;
      }

      setIsSaved(false);

      toast.error(message);
    },
  });

  const unsaveMutation = useMutation({
    mutationFn: unsaveAnime,
    onSuccess: () => {
      toast.success(`${anime.title} unsaved`);
    },
    onError: (error: AxiosError) => {
      let message = error.message;

      if (error.isAxiosError) {
        const axiosError = error as AxiosError<{ message: string }>;
        message = axiosError.response?.data?.message || axiosError.message;
      } else if (error instanceof Error) {
        message = error.message;
      }

      setIsSaved(true);

      toast.error(message);
    },
  });

  const handleSave = () => {
    if (!isSaved) {
      setIsSaved(true);
      saveMutation.mutate(anime.id);
    } else {
      setIsSaved(false);
      unsaveMutation.mutate(anime.id);
    }
  };

  return (
    <div>
      <div className="flex flex-col gap-y-4 max-w-70 mx-auto">
        <div className="relative">
          <AspectRatio ratio={3 / 4}>
            <Image
              src={anime.poster}
              alt={anime.title}
              fill
              className="round-md object-cover"
            />
          </AspectRatio>
          <Tooltip>
            <TooltipTrigger
              asChild
              className="absolute top-1 right-1 cursor-pointer"
            >
              <div
                className="px-1 py-1 rounded-md bg-background/60"
                onClick={(e) => {
                  e.stopPropagation();
                  handleSave();
                }}
              >
                {isSaved ? (
                  <BookmarkIcon
                    className="w-6 h-6 text-indigo-500"
                    fill="currentColor"
                  />
                ) : (
                  <BookmarkIcon className="w-6 h-6" />
                )}
              </div>
            </TooltipTrigger>
            <TooltipContent>
              {isSaved ? "Remove from saved" : "Add to saved"}
            </TooltipContent>
          </Tooltip>
        </div>
        {anime.isFinished ? (
          <Badge
            variant="destructive"
            className="text-xl font-semibold w-full p-3"
          >
            Finished
          </Badge>
        ) : (
          <Badge className="text-xl font-semibold w-full p-3 bg-green-500 dark text-white">
            In emission
          </Badge>
        )}
      </div>
    </div>
  );
}

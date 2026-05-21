"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Item,
  ItemContent,
  ItemDescription,
  ItemGroup,
  ItemTitle,
} from "@/components/ui/item";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent } from "@/components/ui/tooltip";
import apiClient from "@/lib/api-client";
import { EpisodeDownload } from "@/lib/interfaces";
import { TooltipTrigger } from "@radix-ui/react-tooltip";
import { useQuery } from "@tanstack/react-query";
import { DownloadIcon, SearchIcon } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

const apiBaseURL =
  process.env.NODE_ENV === "development"
    ? "http://localhost:4000"
    : "";

const getLastDownloadEpisodes = () => {
  const options = {
    method: "GET",
    url: "/animes/download/last",
  };

  return apiClient(options);
};

interface LastDownloadProps {
  role: string;
  className?: string;
}

export default function LastDownload({ role, className }: LastDownloadProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["last-download"],
    queryFn: () => getLastDownloadEpisodes(),
    refetchOnWindowFocus: false,
  });

  const lastDownloads = data?.data?.payload?.items.slice(0, 4) || [];

  if (isLoading) {
    return (
      <Card className={className}>
        <CardContent className="flex flex-col gap-y-4 lg:gap-y-3">
          <span className="text-sm md:text-base lg:text-lg font-semibold">
            Last Downloaded
          </span>
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-12 lg:h-16 min-w-70 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardContent className="flex flex-col gap-y-4 lg:gap-y-3">
        <span className="text-sm md:text-base lg:text-lg font-semibold">
          Last Downloaded
        </span>
        <ItemGroup className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {lastDownloads?.map((episode: EpisodeDownload) => (
            <Item key={episode.id} variant="outline">
              <Tooltip key={episode.id}>
                <TooltipTrigger>
                  <SearchIcon className="size-5" />
                </TooltipTrigger>
                <TooltipContent className="p-0 m-0 border">
                  <Image
                    src={episode.poster}
                    alt={episode.title}
                    width={150}
                    height={200}
                    className="rounded-md"
                  />
                </TooltipContent>
              </Tooltip>
              <ItemContent>
                <ItemTitle>
                  <Link href={`/anime/${episode.animeId}`}>
                    {episode.title.slice(0, 36)}
                  </Link>
                </ItemTitle>
                <ItemDescription>
                  Episode {episode.episodeNumber}
                </ItemDescription>
              </ItemContent>
              <ItemContent className="">
                <Button
                  variant="ghost"
                  size="icon"
                  disabled={role === "guest"}
                  onClick={() =>
                    (window.location.href = `${apiBaseURL}/api/v1/animes/download/episode/${episode.id}`)
                  }
                  className="cursor-pointer"
                >
                  <DownloadIcon />
                </Button>
              </ItemContent>
            </Item>
          ))}
        </ItemGroup>
      </CardContent>
    </Card>
  );
}

"use client";

import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getMinutesAgo } from "@/lib/utils";
import InformationTab from "./components/information-tab";
import EpisodesTab from "./components/episodes-tab";
import SidebarInfo from "./components/sidebar-info";
import apiClient from "@/lib/api-client";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Spinner } from "@/components/ui/spinner";
import { Skeleton } from "@/components/ui/skeleton";

interface RelatedInfo {
  id: string;
  title: string;
  type: string;
}

interface EpisodeInfo {
  id: number;
  animeId: string;
  imagePreview: string;
  isUserDownloaded: boolean;
  isGlobalDownloaded: boolean;
}

const getAnimeInfo = async (id: string) => {
  const options = {
    method: "GET",
    url: `/animes/info/${id}`,
  };

  return await apiClient(options);
};

const updateAnimeInfo = async (id: string) => {
  const options = {
    method: "PUT",
    url: `/animes/info/${id}`,
  };

  return await apiClient(options);
};

const formatLastUpdate = (lastScrapedAt: string): string => {
  const date = new Date(lastScrapedAt);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMinutes < 60) {
    return `${diffMinutes} minutes ago`;
  } else if (diffDays < 1) {
    const hours = Math.floor(diffMinutes / 60);
    const mins = diffMinutes % 60;
    return `${hours}h ${mins}m ago`;
  } else if (diffDays < 5) {
    const days = diffDays;
    const hours = diffHours % 24;
    return `${days}d ${hours}h ago`;
  } else {
    const day = date.getDate().toString().padStart(2, "0");
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    return `${day} ${month} ${year}`;
  }
};

export interface AnimeInfo {
  id: string;
  title: string;
  type: string;
  poster: string;
  isSaved: boolean;
  season: number;
  platform: string;
  description: string;
  genres: string[];
  relatedInfo: RelatedInfo[];
  weekDay: string;
  episodes: EpisodeInfo[];
  isFinished: boolean;
  lastScrapedAt: string;
}

export default function Anime() {
  const params = useParams();
  const id = params.id as string;
  const [lastUpdateFormatted, setLastUpdateFormatted] = useState<string>("");
  const [minutesToWait, setMinutesToWait] = useState<number | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["anime", id],
    queryFn: () => getAnimeInfo(id),
    refetchOnWindowFocus: false,
  });

  const queryClient = useQueryClient();
  const anime = data?.data?.payload;

  useEffect(() => {
    if (!anime) return;

    const updateTimes = () => {
      setLastUpdateFormatted(formatLastUpdate(anime.lastScrapedAt));
      setMinutesToWait(5 - getMinutesAgo(new Date(anime.lastScrapedAt)));
    };

    updateTimes();
    const interval = setInterval(updateTimes, 60 * 1000);

    return () => clearInterval(interval);
  }, [anime]);

  if (isLoading || !anime || !lastUpdateFormatted || minutesToWait === null) {
    return (
      <>
        <div className="lg:hidden mb-4">
          <span className="text-2xl font-semibold animate-pulse">
            Longs animes will take a long time to load the first time...
          </span>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 px-2 xl:px-12 gap-y-4">
          <div className="flex flex-col gap-y-4 items-center lg:items-start">
            <Skeleton className="w-60 h-96" />
            <Skeleton className="w-60 h-20" />
          </div>
          <div className="flex flex-col col-span-1 lg:col-span-2 xl:col-span-3 gap-y-4">
            <div className="hidden lg:flex flex-row justify-between ">
              <div className="flex flex-col gap-y-4">
                <span className="text-2xl font-semibold animate-pulse  text-wrap">
                  Longs animes will take a long time to load the first time...
                </span>
                <Skeleton className="w-full h-18" />
              </div>
            </div>
            <div className="flex flex-col gap-y-4">
              <div className="flex flex-col gap-y-2">
                <Skeleton className="w-56 h-10" />
                <Skeleton className="w-full h-36" />
              </div>
              <div className="flex flex-col gap-y-2">
                <Skeleton className="w-56 h-10" />
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="w-full sm:w-96 h-10" />
                ))}
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 px-2 gap-x-12 xl:px-12 gap-y-4 pb-20">
      <SidebarInfo anime={anime} />
      <div className="flex flex-col col-span-1 lg:col-span-2 xl:col-span-3 gap-y-4">
        <div className="flex flex-row justify-between">
          <div className="flex flex-col gap-y-1">
            <span className="text-xl md:text-2xl lg:text-3xl font-semibold">
              {anime.title}
            </span>
            <span className="text-sm text-muted-foreground">
              Last update {lastUpdateFormatted}
            </span>
          </div>
          <div className="flex flex-col gap-y-1 justify-center text-center">
            <Button
              variant="destructive"
              className="cursor-pointer"
              disabled={minutesToWait > 0 || isUpdating}
              onClick={async () => {
                setIsUpdating(true);
                try {
                  const freshData = await updateAnimeInfo(id);
                  queryClient.setQueryData(["anime", id], freshData);
                  toast.success("Información actualizada");
                } finally {
                  setIsUpdating(false);
                }
              }}
            >
              {isUpdating ? <Spinner className="mr-2 h-4 w-4 animate-spin" /> : null}
              Update Info
            </Button>
            <span className="text-sm text-muted-foreground">
              {minutesToWait > 0 && `Wait ${minutesToWait} minutes to use`}
            </span>
          </div>
        </div>
        <Tabs defaultValue="information">
          <TabsList className="w-full lg:w-124 h-10">
            <TabsTrigger value="information" className="w-full text-base">
              Information
            </TabsTrigger>
            <TabsTrigger value="episodes" className="w-full text-base">
              Episodes
            </TabsTrigger>
          </TabsList>
          <TabsContent value="information">
            <InformationTab anime={anime} />
          </TabsContent>
          <TabsContent value="episodes">
            <EpisodesTab anime={anime} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

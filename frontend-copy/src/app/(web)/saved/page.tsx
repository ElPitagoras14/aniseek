"use client";

import apiClient from "@/lib/api-client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import AnimeCard, { AnimeInfo } from "@/components/anime-card";
import { ArrowUpNarrowWideIcon, ArrowDownNarrowWideIcon } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const getAnimesSaved = () => {
  const options = {
    method: "GET",
    url: "/animes/saved",
  };

  return apiClient(options);
};

export default function Page() {
  const [sortBy, setSortBy] = useState<string>("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const { data: animesData, isLoading } = useQuery({
    queryKey: ["saved-animes-list"],
    queryFn: getAnimesSaved,
    refetchOnWindowFocus: false,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col gap-y-4">
        <span className="text-xl sm:text-2xl lg:text-3xl font-semibold">
          Saved Animes
        </span>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-x-2 gap-y-6 justify-items-center">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="flex flex-col gap-y-4">
              <Skeleton className="w-38 sm:w-48 h-64 rounded-md" />
              <div className="flex justify-center items-center">
                <Skeleton className="w-38 sm:w-48 h-8" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  console.log(animesData);

  const animes = animesData?.data?.payload?.items || [];

  if (animes.length === 0) {
    return (
      <div className="flex flex-col gap-y-6">
        <span className="text-xl lg:text-3xl font-semibold">
          You haven&apos;t saved any animes yet!
        </span>
      </div>
    );
  }

  const sortedAnimes = animes.sort((a: AnimeInfo, b: AnimeInfo) => {
    const idA = a.id;
    const idB = b.id;

    if (sortBy === "name") {
      if (sortOrder === "asc") {
        return idA.localeCompare(idB);
      } else {
        return idB.localeCompare(idA);
      }
    } else if (sortBy === "save-date") {
      if (sortOrder === "asc") {
        return new Date(a.saveDate).getTime() - new Date(b.saveDate).getTime();
      } else {
        return new Date(b.saveDate).getTime() - new Date(a.saveDate).getTime();
      }
    }
    return 0;
  });

  return (
    <div className="flex flex-col gap-y-4">
      <div className="flex flex-row lg:flex-col justify-between gap-y-2 lg:gap-y-4 items-center lg:items-start">
        <span className="text-xl sm:text-2xl lg:text-3xl font-semibold text-wrap">
          Saved Animes
        </span>
        <div className="flex flex-col gap-y-8">
          <div className="flex flex-row gap-x-2 lg:gap-x-4 items-center">
            <Select value={sortBy} onValueChange={(value) => setSortBy(value)}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Select a sort option" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>Sort by</SelectLabel>
                  <SelectItem value="name">Name</SelectItem>
                  <SelectItem value="save-date">Save date</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
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
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-x-2 gap-y-6 justify-items-center">
        {sortedAnimes.map((item: AnimeInfo) => (
          <AnimeCard key={item.id} animeInfo={item} />
        ))}
      </div>
    </div>
  );
}

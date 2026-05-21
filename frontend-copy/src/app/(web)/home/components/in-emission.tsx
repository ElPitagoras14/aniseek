"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import apiClient from "@/lib/api-client";
import { useQuery } from "@tanstack/react-query";
import { InEmissionAnime } from "../../calendar/page";
import Image from "next/image";
import Link from "next/link";
import { AspectRatio } from "@/components/ui/aspect-ratio";

const getInEmission = () => {
  const options = {
    method: "GET",
    url: "/animes/in-emission",
  };

  return apiClient(options);
};

const weekDays = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];

interface InEmissionProps {
  className?: string;
}

export default function InEmission({ className }: InEmissionProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["in-emission"],
    queryFn: () => getInEmission(),
    refetchOnWindowFocus: false,
  });

  const currentDay = weekDays[new Date().getDay()];
  const animes = data?.data?.payload?.items || [];
  const todaysAnimes = animes.filter((anime: InEmissionAnime) => {
    return anime.weekDay === currentDay;
  });

  if (isLoading) {
    return (
      <Card className={className}>
        <CardContent className="flex flex-col gap-y-4">
          <span className="text-sm md:text-base lg:text-lg font-semibold">
            Today&apos;s Emitted
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-x-4 gap-y-4 justify-items-center">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-46 w-32" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardContent className="flex flex-col gap-y-4">
        <span className="text-sm md:text-base lg:text-lg font-semibold">
          Today&apos;s Emitted
        </span>
        <div className="flex flex-row justify-center">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-x-4 gap-y-4 justify-items-center">
            {todaysAnimes.map(
              (anime: InEmissionAnime) => {
                return (
                  <div
                    className="flex flex-col justify-start items-center gap-y-2"
                    key={anime.id}
                  >
                    <AspectRatio ratio={3 / 4} className="max-w-32 xl:max-w-34 mx-auto">
                      <Link href={`/anime/${anime.id}`}>
                        <Image
                          src={anime.poster}
                          title={anime.title}
                          alt={anime.title}
                          fill
                          className="object-cover rounded-sm"
                        />
                      </Link>
                    </AspectRatio>
                    <span className="text-center text-sm font-semibold w-36">
                      {anime.title}
                    </span>
                  </div>
                );
              }
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

"use client";

import { useEffect, useState } from "react";
import FlowContent from "./flow-content";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import { Button } from "@/components/ui/button";
import { FilePlayIcon } from "lucide-react";
import apiClient from "@/lib/api-client";
import { useQuery } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Spinner } from "@/components/ui/spinner";
import Autocomplete, { Item } from "@/components/autocomplete";
import { Label } from "@/components/ui/label";

export const getFranchises = () => {
  const options = {
    method: "GET",
    url: "/franchises",
  };
  return apiClient(options);
};

export const getAnimesForFranchise = () => {
  const options = {
    method: "GET",
    url: "/franchises/animes",
  };
  return apiClient(options);
};

export interface AnimeFranchise {
  id: string;
  title: string;
  type: string;
  poster: string;
  isSaved: boolean;
  saveDate: string;
  franchise: string | null;
}

export interface Franchise {
  id: string;
  name: string;
  animes: AnimeFranchise[];
}

export default function Season() {
  const [mode, setMode] = useState<"select" | "create">("select");
  const [animeInfo, setAnimeInfo] = useState<Item>({
    value: "",
    label: "",
  });
  const [franchiseInfo, setFranchiseInfo] = useState<Item>({
    value: "",
    label: "",
  });

  const { data: franchisesData, isLoading: franchisesLoading } = useQuery({
    queryKey: ["franchises"],
    queryFn: getFranchises,
    refetchOnWindowFocus: false,
  });

  const franchises = franchisesData?.data?.payload?.items || [];
  const parsedFranchises = franchises.map((franchise: Franchise) => ({
    value: franchise.id,
    label: franchise.name,
  }));

  const { data: animesData, isLoading: animesLoading } = useQuery({
    queryKey: ["animes"],
    queryFn: getAnimesForFranchise,
    refetchOnWindowFocus: false,
  });
  const animes = animesData?.data?.payload?.items || [];
  const parsedAnimes = animes.map((anime: AnimeFranchise) => ({
    value: anime.id,
    label: anime.title,
  }));

  useEffect(() => {
    if (franchiseInfo.value) {
      setAnimeInfo({
        value: "",
        label: "",
      });
    }
  }, [franchiseInfo.value]);

  useEffect(() => {
    if (animeInfo.value) {
      setFranchiseInfo({
        value: "",
        label: "",
      });
    }
  }, [animeInfo.value]);

  const handleClick = () => {
    setMode("create");
  };

  if (franchisesLoading || animesLoading) {
    return (
      <div className="flex flex-row justify-center items-center h-52">
        <Spinner className="size-16" />
      </div>
    );
  }

  if (franchises.length === 0 && mode === "select") {
    return (
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <FilePlayIcon />
          </EmptyMedia>
          <EmptyTitle>No Franchises Yet</EmptyTitle>
          <EmptyDescription>
            You haven&apos;t created any franchise yet. Get started by creating
            your first franchise.
          </EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <Dialog>
            <DialogTrigger>
              <Button className="cursor-pointer">Select an anime</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Select an anime</DialogTitle>
              </DialogHeader>
              <div>
                <Autocomplete
                  items={parsedAnimes}
                  itemInfo={animeInfo}
                  setItemInfo={setAnimeInfo}
                />
              </div>
              <div className="flex flex-row justify-end">
                <Button
                  disabled={!animeInfo.value}
                  onClick={() => setMode("create")}
                >
                  Select
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </EmptyContent>
      </Empty>
    );
  }

  if (franchises.length > 0 && mode === "select") {
    return (
      <div className="flex flex-col px-8 gap-y-6">
        <div className="flex flex-col">
          <span className="text-lg font-semibold">Manage your franchises</span>
          <span className="text-sm text-muted-foreground">
            Select a franchise or anime to start
          </span>
        </div>
        <div className="flex flex-col items-center gap-y-8">
          <div className="flex flex-row justify-center gap-x-12">
            <div className="flex flex-col gap-y-2">
              <Label>Select an existing franchise</Label>
              <Autocomplete
                items={parsedFranchises}
                itemInfo={franchiseInfo}
                setItemInfo={setFranchiseInfo}
                itemName="franchise"
                className="w-80"
              />
            </div>
            <div className="flex flex-col gap-y-2">
              <Label>Start a new franchise</Label>
              <Autocomplete
                items={parsedAnimes}
                itemInfo={animeInfo}
                setItemInfo={setAnimeInfo}
                itemName="anime"
                className="w-80"
              />
            </div>
          </div>
          <Button
            className="cursor-pointer"
            disabled={!franchiseInfo.value && !animeInfo.value}
            onClick={handleClick}
          >
            {franchiseInfo.value && "Manage Franchise"}
            {animeInfo.value && "Create a new franchise"}
            {!franchiseInfo.value && !animeInfo.value && "Choose an option"}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <FlowContent
      baseId={animeInfo.value}
      baseTitle={animeInfo.label}
      setMode={setMode}
    />
  );
}

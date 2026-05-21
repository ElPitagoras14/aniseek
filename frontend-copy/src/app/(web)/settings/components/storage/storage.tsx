"use client";
import { DataTable } from "@/components/data-table/data-table";
import apiClient from "@/lib/api-client";
import { useQuery } from "@tanstack/react-query";
import { getAnimeStorageColumns } from "./columns";

const getAnimesStorage = () => {
  const options = {
    method: "GET",
    url: "/animes/storage",
  };

  return apiClient(options);
};

export default function Storage() {
  const { data, refetch } = useQuery({
    queryKey: ["animes-storage"],
    queryFn: () => getAnimesStorage(),
    refetchOnWindowFocus: false,
  });

  const handleRefetch = async () => {
    await refetch();
  };

  const animes = data?.data?.payload?.items || [];

  const animeStorageColumns = getAnimeStorageColumns({
    refetch: handleRefetch,
  });

  return (
    <DataTable
      columns={animeStorageColumns}
      data={animes}
      enableSelect={false}
    />
  );
}

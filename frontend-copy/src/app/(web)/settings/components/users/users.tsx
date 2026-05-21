"use client";

import { DataTable } from "@/components/data-table/data-table";
import apiClient from "@/lib/api-client";
import { useQuery } from "@tanstack/react-query";
import { userColumns } from "./columns";

const getUsers = async () => {
  const options = {
    method: "GET",
    url: "/users",
  };
  return await apiClient(options);
};

export default function Users() {
  const { data } = useQuery({
    queryKey: ["users"],
    queryFn: () => getUsers(),
    refetchOnWindowFocus: false,
  });

  const items = data?.data?.payload?.items;

  return (
    <DataTable columns={userColumns} data={items || []} enableSelect={false} />
  );
}

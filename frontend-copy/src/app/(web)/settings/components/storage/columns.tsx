"use client";

import { formatSize } from "@/lib/utils";
import { ColumnDef } from "@tanstack/react-table";
import ActionCell from "./action-cell";

type AnimeStorage = {
  id: string;
  title: string;
  size: number;
};

interface AnimeStorageColumnsProps {
  refetch: () => Promise<void>;
}

export const getAnimeStorageColumns = ({
  refetch,
}: AnimeStorageColumnsProps): ColumnDef<AnimeStorage>[] => [
  {
    accessorKey: "title",
    header: "Title",
  },
  {
    accessorKey: "size",
    header: () => <div className="text-center">Size</div>,
    cell: ({
      row: {
        original: { size },
      },
    }) => <div className="text-center">{formatSize(size)}</div>,
  },
  {
    id: "actions",
    header: () => <div className="text-center">Actions</div>,
    cell: ({
      row: {
        original: { id, title },
      },
    }) => <ActionCell animeId={id} title={title} refetch={refetch} />,
  },
];

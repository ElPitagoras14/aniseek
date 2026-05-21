"use client";

import { formatDateTime } from "@/lib/utils";
import { ColumnDef } from "@tanstack/react-table";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import RoleCell from "./role-cell";
import ActiveCell from "./active-cell";
import ActionCell from "./action-celll";

export type User = {
  id: string;
  username: string;
  avatarUrl: string | null;
  avatarLabel: string | null;
  role: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
};

export const userColumns: ColumnDef<User>[] = [
  {
    accessorKey: "avatarUrl",
    header: () => <div className="text-center">Avatar</div>,
    cell: ({
      row: {
        original: { avatarUrl, avatarLabel },
      },
    }) => (
      <div className="flex justify-center">
        <Avatar className="w-28 h-28 p-5">
          <AvatarImage src={avatarUrl || ""} alt={avatarLabel || ""} />
          <AvatarFallback className="text-xl font-semibold">
            {avatarLabel?.toUpperCase() || "N/A"}
          </AvatarFallback>
        </Avatar>
      </div>
    ),
  },
  {
    accessorKey: "username",
    header: () => <div className="text-center">Username</div>,
    cell: ({
      row: {
        original: { username },
      },
    }) => <div className="text-center text-base font-semibold">{username}</div>,
  },
  {
    accessorKey: "role",
    header: () => <div className="text-center">Role</div>,
    cell: ({
      row: {
        original: { role },
      },
    }) => <RoleCell role={role} />,
  },
  {
    accessorKey: "isActive",
    header: () => <div className="text-center">Active</div>,
    cell: ({
      row: {
        original: { isActive },
      },
    }) => <ActiveCell isActive={isActive} />,
  },
  {
    accessorKey: "createdAt",
    header: () => <div className="text-center">Member Since</div>,
    cell: ({
      row: {
        original: { createdAt },
      },
    }) => <div className="text-center">{formatDateTime(createdAt)}</div>,
  },
  {
    accessorKey: "updatedAt",
    header: () => <div className="text-center">Last Updated</div>,
    cell: ({
      row: {
        original: { updatedAt },
      },
    }) => <div className="text-center">{formatDateTime(updatedAt)}</div>,
  },
  {
    id: "actions",
    header: () => <div className="text-center">Actions</div>,
    cell: ({
      row: {
        original: { id, username },
      },
    }) => <ActionCell userId={id} username={username} />,
  },
];

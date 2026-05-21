"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import ChangePassword from "./components/change-password";
import {
  CheckIcon,
  PencilIcon,
  SquareCheckIcon,
  SquareXIcon,
  XIcon,
} from "lucide-react";
import ChangeAvatar from "./components/change-avatar";
import { useEffect, useState } from "react";
import React from "react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useSession } from "next-auth/react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import apiClient from "@/lib/api-client";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { useDebounce } from "use-debounce";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { Spinner } from "@/components/ui/spinner";
import MobileLinks from "./components/mobile-links";

const updateUsername = async (username: string) => {
  const options = {
    method: "PUT",
    url: `/users`,
    data: {
      username,
    },
  };

  return apiClient(options);
};

const checkUsername = async (username: string) => {
  const options = {
    method: "GET",
    url: `/users/username/${username}`,
  };

  return apiClient(options);
};

export default function Profile() {
  const { data: session } = useSession();
  const [username, setUsername] = useState<string | undefined>(
    session?.user.username
  );
  const [editUsername, setEditUsername] = useState<boolean>(false);
  const [usernameDebounced] = useDebounce(username, 500);

  const { update } = useSession();

  const { data, isLoading } = useQuery({
    queryKey: ["username", usernameDebounced],
    queryFn: () => checkUsername(usernameDebounced!),
    refetchOnWindowFocus: false,
    enabled: !!usernameDebounced,
  });

  const usernameAvailable =
    data?.data?.payload || username === session?.user.username;

  const updateUsernameMutation = useMutation({
    mutationFn: updateUsername,
    onError: () => {
      toast.error("Error updating username");
    },
    onSuccess: async () => {
      await update({
        user: {
          ...session?.user,
        },
      });
      toast.success("Username updated successfully");
    },
    onSettled: () => setEditUsername(false),
  });

  useEffect(() => {
    if (session?.user) {
      setUsername(session.user.username);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.user.username]);

  const firstTwoChars = session?.user.username.slice(0, 2);
  const canUpdate = data?.data?.payload && username !== session?.user.username;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="flex flex-col gap-y-6 w-[85%]  lg:w-[65%]">
        <span className="text-3xl font-semibold">Profile</span>
        <div className="flex flex-row items-center gap-x-10">
          <div className="rounded-full bg-muted/20">
            <Avatar className="w-32 h-32 p-5">
              <AvatarImage
                src={session?.user.avatarUrl}
                alt={session?.user.avatarLabel}
              />
              <AvatarFallback className="text-2xl font-semibold">
                {firstTwoChars?.toUpperCase()}
              </AvatarFallback>
            </Avatar>
          </div>
          <ChangeAvatar />
        </div>
        <div className="flex flex-col gap-y-4">
          <Label htmlFor="username">Username</Label>
          <div className="flex gap-x-4 items-center">
            <Input
              id="username"
              placeholder="Username"
              type="text"
              className="w-64"
              value={username || ""}
              onChange={(e) => setUsername(e.target.value)}
              disabled={!editUsername}
            />
            {editUsername && (
              <>
                {isLoading ? (
                  <Spinner className="size-6" />
                ) : canUpdate ? (
                  usernameAvailable ? (
                    <Tooltip>
                      <TooltipTrigger>
                        <CheckIcon className="text-green-500 dark:text-green-400 w-6 h-6" />
                      </TooltipTrigger>
                      <TooltipContent>Username available</TooltipContent>
                    </Tooltip>
                  ) : (
                    <Tooltip>
                      <TooltipTrigger>
                        <XIcon className="text-red-500 dark:text-red-400 w-6 h-6" />
                      </TooltipTrigger>
                      <TooltipContent>Username not available</TooltipContent>
                    </Tooltip>
                  )
                ) : null}
                <Separator orientation="vertical" />
              </>
            )}
            {!editUsername ? (
              <Tooltip>
                <TooltipTrigger>
                  <PencilIcon
                    className="w-6 h-6 cursor-pointer"
                    onClick={() => setEditUsername(true)}
                  />
                </TooltipTrigger>
                <TooltipContent>Edit username</TooltipContent>
              </Tooltip>
            ) : (
              <React.Fragment>
                <SquareXIcon
                  className="w-7 h-7 cursor-pointer text-red-500 dark:text-red-400"
                  onClick={() => {
                    setEditUsername(false);
                    setUsername(session?.user.username);
                  }}
                />
                <SquareCheckIcon
                  className={cn(
                    "w-7 h-7 text-green-500 dark:text-green-400",
                    canUpdate ? "cursor-pointer" : "opacity-50"
                  )}
                  onClick={() =>
                    canUpdate && updateUsernameMutation.mutate(username!)
                  }
                />
              </React.Fragment>
            )}
          </div>
        </div>
        <div className="flex flex-col gap-y-4">
          <Label htmlFor="password">Password</Label>
          <div className="flex">
            <ChangePassword />
          </div>
        </div>
        <MobileLinks className="lg:hidden"/>
      </div>
    </div>
  );
}

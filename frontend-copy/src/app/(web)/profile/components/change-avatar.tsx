"use client";

import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import apiClient from "@/lib/api-client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeftIcon, ArrowRightIcon, XIcon } from "lucide-react";
import { useState } from "react";
import { useSession } from "next-auth/react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface Avatar {
  id: string;
  label: string;
  url: string;
}

const getAvatars = () => {
  const options = {
    method: "GET",
    url: `/users/avatars`,
  };

  return apiClient(options);
};

const updateAvatar = (avatarId: string) => {
  const options = {
    method: "PUT",
    url: `/users`,
    data: {
      avatarId,
    },
  };

  return apiClient(options);
};

export default function ChangeAvatar() {
  const [page, setPage] = useState<number>(0);
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const { data: session, update } = useSession();
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: ["avatars"],
    queryFn: () => getAvatars(),
    refetchOnWindowFocus: false,
  });

  const avatarMutation = useMutation({
    mutationFn: updateAvatar,
    onError: () => {
      toast.error("Error updating avatar");
    },
    onSuccess: async () => {
      await update({
        user: {
          ...session?.user,
        },
      });
      toast.success("Avatar updated successfully");
      setIsOpen(false);
    },
    onSettled: () => {
      queryClient.invalidateQueries({
        queryKey: ["avatars"],
      });
    },
  });

  const items = data?.data?.payload.items || [];

  const pageSize = 12;
  const pages: Avatar[][] = [];

  for (let i = 0; i < items.length; i++) {
    const page = Math.floor(i / pageSize);
    if (pages[page] === undefined) {
      pages[page] = [];
    }
    pages[page].push(items[i]);
  }

  return (
    <AlertDialog
      open={isOpen}
      onOpenChange={(open) => {
        setIsOpen(open);
        setPage(0);
      }}
    >
      <AlertDialogTrigger asChild>
        <Button className="cursor-pointer">Change Avatar</Button>
      </AlertDialogTrigger>
      <AlertDialogContent className="min-h-96 sm:max-w-none w-[95%] lg:w-[70%]">
        <AlertDialogHeader className="flex flex-row justify-between">
          <AlertDialogTitle>Change Avatar</AlertDialogTitle>
          <Button
            variant="ghost"
            size="icon"
            className="cursor-pointer"
            onClick={() => setIsOpen(false)}
          >
            <XIcon className="w-6 lg:w-12 h-6 lg:h-12" />
          </Button>
        </AlertDialogHeader>
        <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-x-12 justify-items-center">
          {pages[page]?.map((avatar: Avatar) => {
            const firstTwoChars = avatar.label.slice(0, 2);
            return (
              <div
                key={avatar.id}
                className={cn(
                  "bg-muted/20 rounded-full cursor-pointer opacity-85",
                  avatarMutation.isPending
                    ? "opacity-50 cursor-not-allowed"
                    : "hover:opacity-100"
                )}
                onClick={() =>
                  !avatarMutation.isPending && avatarMutation.mutate(avatar.id)
                }
              >
                <Avatar key={avatar.id} className="w-26 lg:w-30 h-26 lg:h-30 p-2 lg:p-5">
                  <AvatarImage src={avatar.url} alt={avatar.label} />
                  <AvatarFallback>
                    {firstTwoChars?.toUpperCase()}
                  </AvatarFallback>
                </Avatar>
              </div>
            );
          })}
        </div>
        <AlertDialogFooter className="flex flex-row justify-end gap-x-4">
          <Button
            variant="outline"
            size="icon"
            className="cursor-pointer"
            onClick={() => setPage(page - 1)}
            disabled={page === 0}
          >
            <ArrowLeftIcon className="w-6 h-6" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="cursor-pointer"
            onClick={() => setPage(page + 1)}
            disabled={page === pages.length - 1}
          >
            <ArrowRightIcon className="w-6 h-6" />
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

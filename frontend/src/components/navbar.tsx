"use client";

import {
  BookmarkIcon,
  CalendarIcon,
  HomeIcon,
  SearchIcon,
  TelescopeIcon,
  UserRoundIcon,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ModeToggle } from "@/components/mode-toggle";
import { signOut } from "next-auth/react";

export default function Navbar() {
  const [query, setQuery] = useState<string>("");
  const router = useRouter();

  const redirectToSearch = () => {
    if (!query) {
      return;
    }
    router.push(`/search/${query}`);
  };

  const handleLogout = async () => {
    await signOut({
      redirect: false,
    });
    window.location.href = "/login";
  };

  return (
    <nav className="w-full flex flex-row justify-between py-2 lg:py-3 px-3 lg:px-6 border-b-2 sticky top-0 z-10 bg-background">
      <div className="flex flex-row gap-x-4 items-center">
        <TelescopeIcon className="lg:w-8 lg:h-8 w-6 h-6" />
        <span
          className="text-2xl font-semibold cursor-pointer hidden lg:block"
          onClick={() => router.push("/home")}
        >
          Ani Seek
        </span>
      </div>
      <div className="flex flex-row items-center gap-x-1 lg:gap-x-3.5">
        <Input
          placeholder="Search anime"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              redirectToSearch();
            }
          }}
          className="lg:w-56 lg:h-10 w-48 h-9"
          iconInfo={{
            position: "right",
            icon: SearchIcon,
            fn: () => redirectToSearch(),
          }}
        />
        <div
          className="flex-row items-center gap-x-2 cursor-pointer hover:text-indigo-500 hidden lg:flex"
          onClick={() => router.push("/home")}
        >
          <HomeIcon className="w-6 h-6" />
          <span className="text-base">Home</span>
        </div>
        <div
          className="flex-row items-center gap-x-2 cursor-pointer hover:text-indigo-500 hidden lg:flex"
          onClick={() => router.push("/saved")}
        >
          <BookmarkIcon className="w-6 h-6" />
          <span className="text-base">Saved</span>
        </div>
        <div
          className="flex-row items-center gap-x-2 cursor-pointer hover:text-indigo-500 hidden lg:flex"
          onClick={() => router.push("/calendar")}
        >
          <CalendarIcon className="w-6 h-6" />
          <span className="text-base">Calendar</span>
        </div>
        <Separator orientation="vertical" className="pl-0.5 hidden lg:block" />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <div className="flex-row items-center gap-x-2 cursor-pointer hover:text-indigo-500 hidden lg:flex">
              <UserRoundIcon className="w-6 h-6" />
              <span className="text-base">Profile</span>
            </div>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="start">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuGroup>
              <DropdownMenuItem onClick={() => router.push("/profile")}>
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => router.push("/downloads")}>
                Downloads
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => router.push("/settings")}>
                Settings
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem disabled>API Keys</DropdownMenuItem>
            <DropdownMenuItem onClick={handleLogout}>Log out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <ModeToggle />
      </div>
    </nav>
  );
}

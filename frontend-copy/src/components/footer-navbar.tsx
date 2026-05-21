"use client";

import { BookmarkIcon, CalendarIcon, HomeIcon, UserRoundIcon } from "lucide-react";
import { useRouter } from "next/navigation";

export default function FooterNavbar() {
  const router = useRouter();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-background border-t-2 lg:hidden z-10">
      <div className="flex justify-around py-2">
        <div
          className="flex flex-col items-center gap-y-1 cursor-pointer hover:text-indigo-500"
          onClick={() => router.push("/home")}
        >
          <HomeIcon className="w-6 h-6" />
          <span className="text-xs">Home</span>
        </div>
        <div
          className="flex flex-col items-center gap-y-1 cursor-pointer hover:text-indigo-500"
          onClick={() => router.push("/saved")}
        >
          <BookmarkIcon className="w-6 h-6" />
          <span className="text-xs">Saved</span>
        </div>
        <div
          className="flex flex-col items-center gap-y-1 cursor-pointer hover:text-indigo-500"
          onClick={() => router.push("/calendar")}
        >
          <CalendarIcon className="w-6 h-6" />
          <span className="text-xs">Calendar</span>
        </div>
        <div
          className="flex flex-col items-center gap-y-1 cursor-pointer hover:text-indigo-500"
          onClick={() => router.push("/profile")}
        >
          <UserRoundIcon className="w-6 h-6" />
          <span className="text-xs">Profile</span>
        </div>
      </div>
    </nav>
  );
}

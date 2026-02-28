"use client";

import { TelescopeIcon } from "lucide-react";
import Link from "next/link";
import { ModeToggle } from "@/components/mode-toggle";
import { Button } from "@/components/ui/button";

export default function LandingNavbar() {
  return (
    <nav className="w-full flex flex-row justify-between py-3 px-4 lg:px-8 border-b sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex flex-row gap-x-3 items-center">
        <TelescopeIcon className="w-7 h-7" />
        <span
          className="text-xl font-semibold cursor-pointer"
          onClick={() => (window.location.href = "/")}
        >
          Aniseek
        </span>
      </div>
      <div className="flex flex-row items-center gap-x-3">
        <Button variant="ghost" asChild>
          <Link href="/login">Login</Link>
        </Button>
        <Button asChild>
          <Link href="/register">Register</Link>
        </Button>
        <ModeToggle />
      </div>
    </nav>
  );
}

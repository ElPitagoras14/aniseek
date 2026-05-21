"use client";

import { cn } from "@/lib/utils";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

interface ModeToggleProps {
  className?: string;
}

export function ModeToggle({ className }: ModeToggleProps) {
  const { setTheme, theme } = useTheme();

  const toggle = () => {
    setTheme(theme === "light" ? "dark" : "light");
  };

  return (
    <div
      className={cn("hover:bg-accent p-2 rounded-md cursor-pointer", className)}
      onClick={toggle}
    >
      {theme === "light" ? (
        <Moon className="h-5 w-5 scale-100 rotate-0 transition-all" />
      ) : (
        <Sun className="h-5 w-5 scale-100 rotate-0 transition-all" />
      )}
      <span className="sr-only">Toggle theme</span>
    </div>
  );
}

import * as React from "react";

import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  iconInfo?: {
    position: "left" | "right";
    icon: LucideIcon;
    fn: () => void;
  };
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, iconInfo, ...props }, ref) => (
    <div className="relative">
      {iconInfo && iconInfo.position === "left" && (
        <div className="absolute inset-y-0 end-3 flex items-center ps-3">
          <iconInfo.icon
            className="h-5 w-5 text-muted-foreground hover:cursor-pointer z-20"
            onClick={iconInfo.fn}
          />
        </div>
      )}
      <input
        type={type}
        className={cn(
          "block h-10 border border-input rounded-md bg-background w-full px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
      {iconInfo && iconInfo.position === "right" && (
        <div className="absolute inset-y-0 end-3 flex items-center ps-3">
          <iconInfo.icon
            className="lg:h-5 lg:w-5 h-4 w-4 text-muted-foreground hover:cursor-pointer z-20"
            onClick={iconInfo.fn}
          />
        </div>
      )}
    </div>
  )
);
Input.displayName = "Input";

export { Input };

import { ArrowRight } from "lucide-react";
import Link from "next/link";

interface MobileLinksProps {
  className?: string;
}

export default function MobileLinks({ className }: MobileLinksProps) {
  return (
    <div className={className}>
      <div className="flex flex-col gap-y-4">
        <Link href="/downloads" className="flex flex-row gap-x-2 items-center">
          <span className="text-lg font-semibold">Downloads</span>
          <ArrowRight className="w-6 h-6" />
        </Link>
      </div>
    </div>
  );
}

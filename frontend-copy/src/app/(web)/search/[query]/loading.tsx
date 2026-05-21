import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <div className="flex flex-col gap-y-4 lg:gap-y-10">
      <span className="text-xl lg:text-3xl font-semibold">Search results</span>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-x-2 gap-y-6 justify-items-center">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex flex-col gap-y-4">
            <Skeleton className="w-38 sm:w-48 h-64 rounded-md" />
            <div className="flex justify-center items-center">
              <Skeleton className="w-38 sm:w-48 h-8" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

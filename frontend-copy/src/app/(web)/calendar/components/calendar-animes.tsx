import Link from "next/link";
import { InEmissionAnime } from "../page";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import Image from "next/image";

interface CalendarAnimesProps {
  animes: InEmissionAnime[];
}

export default function CalendarAnimes({ animes }: CalendarAnimesProps) {
  if (!animes) {
    return null;
  }

  return (
    <div className="flex flex-col justify-start">
      {animes.map((anime) => {
        const { id, title, poster } = anime;
        return (
          <Tooltip key={id}>
            <TooltipTrigger>
              <Link href={`/anime/${id}`} key={id}>
                <div className="p-2 m-1 rounded-sm bg-accent/50 hover:bg-accent hover:cursor-pointer text-wrap">
                  {title}
                </div>
              </Link>
            </TooltipTrigger>
            <TooltipContent className="p-0 m-0 border">
              <div className="flex flex-row gap-x-2">
                <Image
                  src={poster}
                  alt={title}
                  width={200}
                  height={200}
                  className="rounded-md"
                />
              </div>
            </TooltipContent>
          </Tooltip>
        );
      })}
    </div>
  );
}

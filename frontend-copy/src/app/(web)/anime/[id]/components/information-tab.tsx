import { Badge } from "@/components/ui/badge";
import { AnimeInfo } from "../page";
import Link from "next/link";

interface InformationTabProps {
  anime: AnimeInfo;
}

export default function InformationTab({ anime }: InformationTabProps) {
  return (
    <div className="flex flex-col gap-y-4">
      <div className="flex flex-col gap-y-2">
        <span className="text-lg font-semibold">Synopsis</span>
        <p className="text-base text-muted-foreground">{anime.description}</p>
      </div>
      <div className="flex flex-col gap-y-2">
        <span className="text-lg font-semibold">Genres</span>
        <div className="flex flex-row flex-wrap gap-x-2">
          {anime.genres.map((genre) => (
            <Badge key={genre} className="py-1 px-4 text-sm">
              {genre}
            </Badge>
          ))}
        </div>
      </div>
      <div className="flex flex-col gap-y-2">
        <span className="text-lg font-semibold">Related info</span>
        <ul className="flex flex-col gap-y-2">
          {anime.relatedInfo.map((info) => (
            <li key={info.id} className="flex flex-row gap-x-2">
              <Link
                href={`/anime/${info.id}`}
                className="text-muted-foreground hover:text-indigo-400"
              >
                {info.title}
              </Link>
              <Badge>{info.type}</Badge>
            </li>
          ))}
        </ul>
      </div>

    </div>
  );
}

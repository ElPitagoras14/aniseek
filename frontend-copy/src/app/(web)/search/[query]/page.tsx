import AnimeCard, { AnimeInfo } from "@/components/anime-card";
import { getApiServer } from "@/lib/api-server";

interface PageProps {
  params: Promise<{
    query: string;
  }>;
}

export default async function Page({ params }: PageProps) {
  const { query } = await params;

  const apiServer = await getApiServer();

  const options = {
    method: "GET",
    url: "/animes/search",
    params: {
      query: query,
    },
  };

  const response = await apiServer(options);
  const {
    data: {
      payload: { items },
    },
  } = response;

  const decoded = decodeURIComponent(query);

  return (
    <div className="flex flex-col gap-y-4 lg:gap-y-10">
      <span className="text-xl lg:text-3xl font-semibold">
        Search results for &quot;{decoded}&quot;
      </span>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-x-2 gap-y-6 justify-items-center">
        {items.map((item: AnimeInfo) => (
          <AnimeCard key={item.id} animeInfo={item} />
        ))}
      </div>
    </div>
  );
}

import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { Bookmark, CalendarClock, Download } from "lucide-react";
import {
	statisticsQueryOptions,
	storageQueryOptions,
} from "@/features/home/api";
import { HomeKpi } from "@/features/home/components/home-kpi";
import { HomeLastDownloads } from "@/features/home/components/home-last-downloads";
import { HomeStorage } from "@/features/home/components/home-storage";
import { HomeTodayCalendar } from "@/features/home/components/home-today-calendar";
import { HomeWelcome } from "@/features/home/components/home-welcome";

export const Route = createFileRoute("/_app/home")({
	component: RouteComponent,
});

function RouteComponent() {
	const statistics = useQuery(statisticsQueryOptions);
	const storage = useQuery(storageQueryOptions({ page: 1, limit: 10 }));

	return (
		<div className="p-4 md:p-6 lg:p-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6">
			<HomeWelcome className="col-span-1 sm:col-span-2 lg:col-span-2" />
			<HomeKpi
				className="col-span-1 sm:col-span-2 lg:col-span-2"
				label="Downloaded episodes"
				value={statistics.data?.downloadedEpisodes}
				isLoading={statistics.isLoading}
				isError={statistics.isError}
				url="/downloads"
				icon={Download}
				iconClassName="text-sky-500"
			/>
			<HomeStorage
				className="col-span-1 sm:col-span-2 lg:col-span-2 lg:row-span-2"
				data={storage.data}
				isLoading={storage.isLoading}
				isError={storage.isError}
				onRetry={() => storage.refetch()}
			/>
			<HomeKpi
				className="col-span-1 sm:col-span-2 lg:col-span-2"
				label="Saved animes"
				value={statistics.data?.savedAnimes}
				isLoading={statistics.isLoading}
				isError={statistics.isError}
				url="/saved"
				icon={Bookmark}
				iconClassName="text-emerald-500"
			/>
			<HomeKpi
				className="col-span-1 sm:col-span-2 lg:col-span-2"
				label="In emission"
				value={statistics.data?.inEmissionAnimes}
				isLoading={statistics.isLoading}
				isError={statistics.isError}
				url="/calendar"
				icon={CalendarClock}
				iconClassName="text-amber-500"
			/>
			<HomeTodayCalendar className="col-span-1 sm:col-span-2 lg:col-span-3 lg:row-span-2" />
			<HomeLastDownloads className="col-span-1 sm:col-span-2 lg:col-span-3 lg:row-span-2" />
		</div>
	);
}

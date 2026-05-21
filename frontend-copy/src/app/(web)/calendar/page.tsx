import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getApiServer } from "@/lib/api-server";
import CalendarAnimes from "./components/calendar-animes";

const weekDays = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

export interface InEmissionAnime {
  id: string;
  title: string;
  type: string;
  poster: string;
  isSaved: boolean;
  saveDate: string;
  weekDay: string;
}

const getAnimesByWeekDay = (animes: InEmissionAnime[]) => {
  const indexedByWeekDay: Record<string, InEmissionAnime[]> = {};

  animes.forEach((anime) => {
    if (!indexedByWeekDay[anime.weekDay]) {
      indexedByWeekDay[anime.weekDay] = [];
    }
    indexedByWeekDay[anime.weekDay].push(anime);
  });

  return indexedByWeekDay;
};

export default async function Calendar() {
  const apiServer = await getApiServer();

  const options = {
    method: "GET",
    url: "/animes/in-emission",
  };

  const response = await apiServer(options);
  const {
    data: {
      payload: { items },
    },
  } = response;

  const indexedByWeekDay = getAnimesByWeekDay(items);

  return (
    <div className="flex flex-col gap-y-10">
      <span className="text-3xl font-semibold">Emission Calendar</span>
      <Table>
        <TableHeader>
          <TableRow>
            {weekDays.map((weekDay) => {
              return (
                <TableHead
                  key={`${weekDay}-header`}
                  className="border text-center w-[14.28%]"
                >
                  {weekDay}
                </TableHead>
              );
            })}
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow className="hover:bg-background">
            {weekDays.map((weekDay) => {
              return (
                <TableCell
                  key={weekDay}
                  className="border m-0 p-0 align-top"
                >
                  <CalendarAnimes animes={indexedByWeekDay[weekDay]} />
                </TableCell>
              );
            })}
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}

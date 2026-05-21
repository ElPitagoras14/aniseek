import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const allWeekDays = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

export default function CalendarLoading() {
  return (
    <div className="flex flex-col gap-y-10">
      <span className="text-3xl font-semibold">Emission Calendar</span>
      <Table className="border rounded-sm">
        <TableHeader>
          <TableRow>
            {allWeekDays.map((weekDay) => {
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
            {allWeekDays.map((weekDay) => {
              return (
                <TableCell
                  key={weekDay}
                  className="border text-wrap m-0 p-0 align-top"
                >
                  <div className="m-1 h-8">
                    <Skeleton className="w-full h-full"></Skeleton>
                  </div>
                </TableCell>
              );
            })}
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}

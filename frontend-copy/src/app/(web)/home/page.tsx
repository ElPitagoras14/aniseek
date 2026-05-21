import LastDownload from "./components/last-download";
import { auth } from "@/auth";
import Statistics from "./components/statistics";
import InEmission from "./components/in-emission";

export default async function Home() {
  const session = await auth();

  if (!session?.user) return null;

  return (
    <div className="flex justify-center">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 w-auto">
        <Statistics />
        <LastDownload role={session.user.role} className="lg:col-span-3" />
        <InEmission className="lg:col-span-4" />
      </div>
    </div>
  );
}

import { Spinner } from "@/components/ui/spinner";

export default async function Page() {
  return (
    <div className="flex flex-col h-svh justify-center items-center gap-y-4">
      <Spinner className="size-20"/>
    </div>
  );
}

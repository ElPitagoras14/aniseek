import { DownloadProgressProvider } from "@/providers/progress-provider";

export default function DownloadLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DownloadProgressProvider>{children}</DownloadProgressProvider>;
}

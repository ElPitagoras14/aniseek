import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const getMinutesAgo = (date: Date): number => {
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  const minutes = Math.floor(seconds / 60);
  return minutes;
};

export const formatSize = (sizeInBytes: number | null | undefined): string => {
  if (!sizeInBytes) {
    return "0 MB";
  }
  if (sizeInBytes < 1024) {
    return `${sizeInBytes} B`;
  } else if (sizeInBytes < 1024 ** 2) {
    return `${(sizeInBytes / 1024).toFixed(2)} KB`;
  } else if (sizeInBytes < 1024 ** 3) {
    return `${(sizeInBytes / 1024 ** 2).toFixed(2)} MB`;
  } else if (sizeInBytes < 1024 ** 4) {
    return `${(sizeInBytes / 1024 ** 3).toFixed(2)} GB`;
  } else {
    return `${(sizeInBytes / 1024 ** 4).toFixed(2)} TB`;
  }
};

export const formatDateTime = (utcDateString: string): string => {
  if (!utcDateString) return "N/A";

  try {
    const dateString = utcDateString.endsWith("Z")
      ? utcDateString
      : utcDateString + "Z";

    const date = new Date(dateString);

    if (isNaN(date.getTime())) {
      return "Fecha inválida";
    }

    return date.toLocaleString("es-ES", {
      hour12: false,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch (error) {
    console.error("Error formatting date:", error);
    return "Fecha inválida";
  }
};

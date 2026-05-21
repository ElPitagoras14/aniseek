import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { ChevronsUpDownIcon, CheckIcon } from "lucide-react";
import { useState } from "react";
import { Item } from "@/components/autocomplete";
import { AnimeFranchise } from "./season";

interface AutocompleteAnimeProps {
  animes: AnimeFranchise[];
  animeInfo: Item;
  setAnimeInfo: (animeInfo: Item) => void;
}

export default function AutocompleteAnime({
  animes,
  animeInfo,
  setAnimeInfo,
}: AutocompleteAnimeProps) {
  const [open, setOpen] = useState<boolean>(false);

  const parsedAnimes = animes.map((anime) => ({
    value: anime.id,
    label: anime.title,
  }));

  const height = animeInfo.value.length > 42 ? "h-14" : "h-10";

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={`w-full justify-between ${height}`}
        >
          {animeInfo.value ? (
            <p className="text-wrap text-start">
              {
                parsedAnimes.find((anime) => anime.value === animeInfo.value)
                  ?.label
              }
            </p>
          ) : (
            "Select anime..."
          )}
          <ChevronsUpDownIcon className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0">
        <Command>
          <CommandInput placeholder="Search anime..." />
          <CommandList>
            <CommandEmpty>No anime found.</CommandEmpty>
            <CommandGroup>
              {parsedAnimes.map((anime) => (
                <CommandItem
                  key={anime.value}
                  value={anime.value}
                  onSelect={(currentValue) => {
                    setAnimeInfo(
                      currentValue === animeInfo.value
                        ? {
                            value: "",
                            label: "",
                          }
                        : {
                            value: currentValue,
                            label: animes.find(
                              (anime) => anime.id === currentValue
                            )!.title,
                          }
                    );
                    setOpen(false);
                  }}
                >
                  <CheckIcon
                    className={cn(
                      "mr-2 h-4 w-4",
                      animeInfo.value === anime.value
                        ? "opacity-100"
                        : "opacity-0"
                    )}
                  />
                  {anime.label}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

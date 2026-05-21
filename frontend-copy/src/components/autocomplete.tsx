import { cn } from "@/lib/utils";
import { ChevronsUpDownIcon, CheckIcon } from "lucide-react";
import { useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";

export interface Item {
  value: string;
  label: string;
}

interface AutocompleteProps {
  items: Item[];
  itemInfo: Item;
  setItemInfo: (itemInfo: Item) => void;
  itemName?: string;
  className?: string;
}

export default function Autocomplete({
  items,
  itemInfo,
  setItemInfo,
  itemName = "item",
  className,
}: AutocompleteProps) {
  const [open, setOpen] = useState<boolean>(false);

  const height = itemInfo.value.length > 42 ? "h-14" : "h-10";

  return (
    <div className={className}>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className={`w-full justify-between ${height}`}
          >
            {itemInfo.value ? (
              <p className="text-wrap text-start">
                {items.find((item) => item.value === itemInfo.value)?.label}
              </p>
            ) : (
              `Select ${itemName}...`
            )}
            <ChevronsUpDownIcon className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-full p-0">
          <Command>
            <CommandInput placeholder={`Search ${itemName}...`} />
            <CommandList>
              <CommandEmpty>No {itemName} found.</CommandEmpty>
              <CommandGroup>
                {items.map((item) => (
                  <CommandItem
                    key={item.value}
                    value={item.value}
                    onSelect={(currentValue) => {
                      setItemInfo(
                        currentValue === itemInfo.value
                          ? {
                              value: "",
                              label: "",
                            }
                          : {
                              value: currentValue,
                              label: items.find(
                                (item) => item.value === currentValue
                              )!.label,
                            }
                      );
                      setOpen(false);
                    }}
                  >
                    <CheckIcon
                      className={cn(
                        "mr-2 h-4 w-4",
                        itemInfo.value === item.value
                          ? "opacity-100"
                          : "opacity-0"
                      )}
                    />
                    {item.label}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}

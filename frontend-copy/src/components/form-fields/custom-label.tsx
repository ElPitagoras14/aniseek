import { FormLabel } from "@/components/ui/form";
import { Tooltip, TooltipContent, TooltipTrigger } from "../ui/tooltip";
import { InfoIcon } from "lucide-react";

interface CustomLabelProps {
  label: string;
  description?: string;
}

export default function CustomLabel({ label, description }: CustomLabelProps) {
  if (!description) {
    return <FormLabel>{label}</FormLabel>;
  }

  return (
    <div className="flex items-center space-x-1">
      <FormLabel>{label}</FormLabel>
      <Tooltip>
        <TooltipTrigger>
          <InfoIcon className="w-4 h-4" />
        </TooltipTrigger>
        <TooltipContent>{description}</TooltipContent>
      </Tooltip>
    </div>
  );
}

import { Switch } from "@/components/ui/switch";
import { useState } from "react";

interface ActiveCellProps {
  isActive: boolean;
}

export default function ActiveCell({ isActive }: ActiveCellProps) {
  const [currIsActive, setCurrIsActive] = useState<boolean>(isActive);

  return (
    <div className="flex justify-center items-center">
      <Switch
        checked={currIsActive}
        onCheckedChange={(value: boolean) => setCurrIsActive(value)}
      ></Switch>
    </div>
  );
}

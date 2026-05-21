import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";

interface RoleCellProps {
  role: string;
}

export default function RoleCell({ role }: RoleCellProps) {
  const [currRole, setCurrRole] = useState<string>(role);

  return (
    <div className="flex flex-row justify-center">
      <Select value={currRole} onValueChange={(value) => setCurrRole(value)}>
        <SelectTrigger>
          <SelectValue placeholder="Select a role" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Roles</SelectLabel>
            <SelectItem value="guest">Guest</SelectItem>
            <SelectItem value="member">Member</SelectItem>
            <SelectItem value="admin">Admin</SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  );
}

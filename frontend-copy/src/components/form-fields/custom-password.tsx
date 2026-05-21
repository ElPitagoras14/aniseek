"use client";

import { PasswordField } from "@/lib/interfaces";
import { ControllerRenderProps } from "react-hook-form";
import { FormControl, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import CustomLabel from "@/components/form-fields/custom-label";

interface CustomPasswordProps {
  fieldInfo: PasswordField;
  field: ControllerRenderProps;
}

export default function CustomPassword({
  fieldInfo,
  field,
}: CustomPasswordProps) {
  const { label, placeholder, description } = fieldInfo;

  const [showPassword, setShowPassword] = useState<boolean>(false);

  return (
    <>
      {label && <CustomLabel label={label} description={description} />}
      <FormControl>
        <Input
          {...field}
          placeholder={placeholder}
          type={showPassword ? "text" : "password"}
          iconInfo={{
            position: "right",
            icon: showPassword ? EyeOff : Eye,
            fn: () => {
              setShowPassword(!showPassword);
            },
          }}
        />
      </FormControl>
      <FormMessage />
    </>
  );
}

import { TextField } from "@/lib/interfaces";
import { ControllerRenderProps } from "react-hook-form";
import { FormControl, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import CustomLabel from "@/components/form-fields/custom-label";

interface CustomTextProps {
  fieldInfo: TextField;
  field: ControllerRenderProps;
  inputClassName?: string;
}

export default function CustomText({ fieldInfo, field, inputClassName }: CustomTextProps) {
  const { label, placeholder, description } = fieldInfo;

  return (
    <>
      {label && <CustomLabel label={label} description={description} />}
      <FormControl>
        <Input placeholder={placeholder} {...field} className={inputClassName} />
      </FormControl>
      <FormMessage />
    </>
  );
}

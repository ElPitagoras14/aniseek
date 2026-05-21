import { UseFormReturn } from "react-hook-form";
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { FieldInfo } from "@/lib/interfaces";
import CustomText from "@/components/form-fields/custom-text";
import CustomPassword from "@/components/form-fields/custom-password";

interface CustomFieldProps {
  form: UseFormReturn;
  fieldInfo: FieldInfo;
  className?: string;
  inputClassName?: string;
}

export default function CustomField({
  form,
  fieldInfo,
  className,
  inputClassName,
}: CustomFieldProps) {
  const { name, label, placeholder, description, type } = fieldInfo;

  if (type === "text") {
    return (
      <FormField
        control={form.control}
        name={name}
        render={({ field }) => (
          <FormItem className={className}>
            <CustomText fieldInfo={fieldInfo} field={field} inputClassName={inputClassName}></CustomText>
          </FormItem>
        )}
      />
    );
  }

  if (type === "number") {
    return (
      <FormField
        control={form.control}
        name={name}
        render={({ field }) => (
          <FormItem className={className}>
            <FormLabel>{label}</FormLabel>
            <FormControl>
              <Input placeholder={placeholder} {...field} />
            </FormControl>
            <FormDescription>{description}</FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    );
  }

  if (type === "password") {
    return (
      <FormField
        control={form.control}
        name={name}
        render={({ field }) => (
          <FormItem className={className}>
            <CustomPassword fieldInfo={fieldInfo} field={field} />
          </FormItem>
        )}
      />
    );
  }
}

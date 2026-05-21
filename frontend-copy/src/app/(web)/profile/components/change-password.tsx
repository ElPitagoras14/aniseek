"use client";

import CustomField from "@/components/form-fields/custom-field";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Form } from "@/components/ui/form";
import apiClient from "@/lib/api-client";
import { FormField } from "@/lib/interfaces";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useSession } from "next-auth/react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const fields: FormField[] = [
  {
    name: "currentPassword",
    label: "Current Password",
    type: "password",
    validation: z.string().min(4, "Password must be at least 6 characters"),
  },
  {
    name: "newPassword",
    label: "New Password",
    type: "password",
    validation: z.string().min(6, "Password must be at least 6 characters"),
  },
  {
    name: "confirmPassword",
    label: "Confirm Password",
    type: "password",
    validation: z.string().min(6, "Password must be at least 6 characters"),
  },
];

const formSchema = z
  .object(
    fields.reduce((acc, field) => {
      acc[field.name] = field.validation;
      return acc;
    }, {} as Record<string, z.ZodType>)
  )
  .refine(
    (data) => {
      return data.newPassword === data.confirmPassword;
    },
    {
      message: "Passwords do not match",
    }
  );

interface PasswordInfo {
  currentPass: string;
  newPass: string;
}

const updateAvatar = ({ currentPass, newPass }: PasswordInfo) => {
  const options = {
    method: "PUT",
    url: `/users`,
    data: {
      password: {
        currentPassword: currentPass,
        newPassword: newPass,
      },
    },
  };

  return apiClient(options);
};

export default function ChangePassword() {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const { data: session, update } = useSession();

  const passwordMutation = useMutation({
    mutationFn: updateAvatar,
    onError: () => {
      toast.error("Error updating password");
    },
    onSuccess: async () => {
      await update({
        user: {
          ...session?.user,
        },
      });
      toast.success("Password updated successfully");
      setIsOpen(false);
    },
  });

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    },
  });

  const onSubmit = form.handleSubmit((values: z.infer<typeof formSchema>) => {
    passwordMutation.mutate({
      currentPass: values.currentPassword as string,
      newPass: values.newPassword as string,
    });
  });

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) {
          form.reset();
        }
        setIsOpen(open);
      }}
    >
      <DialogTrigger asChild>
        <Button variant="outline" className="cursor-pointer">
          Change Password
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Change Password</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form className="flex flex-col gap-6">
            {fields.map((field) => (
              <CustomField key={field.name} form={form} fieldInfo={field} />
            ))}
          </form>
        </Form>
        <DialogFooter className="flex flex-row justify-end gap-x-4">
          <Button
            variant="outline"
            className="cursor-pointer"
            onClick={() => setIsOpen(false)}
          >
            Cancel
          </Button>
          <Button className="cursor-pointer" onClick={onSubmit}>
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

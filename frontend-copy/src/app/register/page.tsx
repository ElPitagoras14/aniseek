"use client";

import { TelescopeIcon } from "lucide-react";
import Link from "next/link";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { FormField } from "@/lib/interfaces";
import { Form } from "@/components/ui/form";
import { SiGithub, SiBuymeacoffee } from "@icons-pack/react-simple-icons";
import CustomField from "@/components/form-fields/custom-field";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { AxiosError } from "axios";
import apiClient from "@/lib/api-client";
import { Spinner } from "@/components/ui/spinner";

const fields: FormField[] = [
  {
    name: "username",
    label: "Username",
    placeholder: "shadcn",
    type: "text",
    validation: z.string().min(2, {
      message: "Username must be at least 2 characters long",
    }),
  },
  {
    name: "password",
    label: "Password",
    placeholder: "********",
    type: "password",
    validation: z.string().min(2, {
      message: "Password must be at least 2 characters long",
    }),
  },
  {
    name: "confirmPassword",
    label: "Confirm Password",
    placeholder: "********",
    type: "password",
    validation: z.string().min(2, {
      message: "Password must be at least 2 characters long",
    }),
  },
];

const formSchema = z
  .object(
    fields.reduce((acc, field) => {
      acc[field.name] = field.validation;
      return acc;
    }, {} as Record<string, z.ZodType>)
  )
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

const createUser = async (values: z.infer<typeof formSchema>) => {
  const options = {
    method: "POST",
    url: "/auth/register",
    data: {
      username: values.username,
      password: values.password,
    },
  };

  return await apiClient(options);
};

export default function Login() {
  const router = useRouter();

  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      toast.success("User created successfully");
      router.push("/login");
    },
    onError: (error: AxiosError) => {
      let message = error.message;

      if (error.isAxiosError) {
        const axiosError = error as AxiosError<{ message: string }>;
        message = axiosError.response?.data?.message || axiosError.message;
      } else if (error instanceof Error) {
        message = error.message;
      }

      toast.error(message);
    },
  });

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "admin",
      password: "admin",
      confirmPassword: "admin",
    },
  });

  const onSubmit = form.handleSubmit(
    async (values: z.infer<typeof formSchema>) => {
      try {
        mutation.mutate(values);
      } catch (error) {
        console.log(error);
      }
    }
  );

  return (
    <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="w-full max-w-sm">
        <Form {...form}>
          <form className="flex flex-col gap-6 px-4">
            <div className="flex flex-col items-center gap-2">
              <TelescopeIcon className="w-8 h-8" />
              <h1 className="text-3xl font-bold">Join to Ani Seek</h1>
              <span className="text-xl text-muted-foreground">
                Create an account and start exploring
              </span>
              <div className="text-center text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link
                  href="/login"
                  className="underline underline-offset-4 text-primary"
                >
                  Sign in
                </Link>
              </div>
            </div>
            <div className="flex flex-col gap-2">
              {fields.map((field) => (
                <CustomField key={field.name} form={form} fieldInfo={field} />
              ))}
            </div>
            <Button type="button" className="cursor-pointer" onClick={onSubmit}>
              Register{" "}
              {mutation.isPending && (
                <Spinner className="size-5" />
              )}
            </Button>
            <div className="flex justify-center gap-4">
              <Link
                href="https://github.com/ElPitagoras14"
                target="_blank"
                className="flex items-center gap-2"
              >
                <SiGithub />
                <span>Github</span>
              </Link>
              <Link
                href="https://buymeacoffee.com/jhonyg"
                target="_blank"
                className="flex items-center gap-2"
              >
                <SiBuymeacoffee />
                <span>Support it</span>
              </Link>
            </div>
          </form>
        </Form>
      </div>
    </div>
  );
}

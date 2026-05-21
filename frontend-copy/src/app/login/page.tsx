"use client";

import { CopyIcon, TelescopeIcon } from "lucide-react";
import Link from "next/link";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { FormField } from "@/lib/interfaces";
import { Form } from "@/components/ui/form";
import { SiGithub, SiBuymeacoffee } from "@icons-pack/react-simple-icons";
import CustomField from "@/components/form-fields/custom-field";
import { useState } from "react";
import { signIn } from "next-auth/react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
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
];

const formSchema = z.object(
  fields.reduce((acc, field) => {
    acc[field.name] = field.validation;
    return acc;
  }, {} as Record<string, z.ZodType>)
);

export default function Login() {
  const [isLoading, setIsloading] = useState<boolean>(false);

  const router = useRouter();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const onSubmit = form.handleSubmit(
    async (values: z.infer<typeof formSchema>) => {
      try {
        setIsloading(true);
        const response = await signIn("credentials", {
          username: values.username,
          password: values.password,
          redirect: false,
        });

        if (response?.error) {
          if (response.error === "CredentialsSignin") {
            toast.error("Invalid username or password");
          } else {
            toast.error("Something went wrong");
          }
        } else if (response?.ok) {
          toast.success("Logged in successfully");
          router.push("/home");
        }
      } catch (error) {
        console.log(error);
      } finally {
        setIsloading(false);
      }
    }
  );

  const copyToClipboard = async (text: string) => {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(text);
        toast.success("Copied to clipboard");
      } catch {
        toast.error("Failed to copy");
      }
    } else {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();

      try {
        document.execCommand("copy");
        toast.success("Copied to clipboard");
      } catch {
        toast.error("Failed to copy");
      } finally {
        document.body.removeChild(textarea);
      }
    }
  };

  return (
    <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="w-full max-w-sm">
        <Form {...form}>
          <form className="flex flex-col gap-6 px-4">
            <div className="flex flex-col items-center gap-2">
              <TelescopeIcon className="w-8 h-8" />
              <h1 className="text-3xl font-bold">Welcome to Ani Seek</h1>
              <span className="text-xl text-muted-foreground">
                A simple way to scrap anime
              </span>
              <div className="text-center text-sm text-muted-foreground">
                Don&apos;t have an account?{" "}
                <Link
                  href="/register"
                  className="underline underline-offset-4 text-primary"
                >
                  Sign up
                </Link>
              </div>
            </div>
            <Accordion type="single" collapsible>
              <AccordionItem value="guest">
                <AccordionTrigger className="cursor-pointer">
                  <span className="text-base font-semibold">Guest User</span>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="flex flex-col gap-y-2">
                    <div className="flex justify-between py-2 px-2 bg-muted/50 rounded-md">
                      <span className="text-sm">
                        <span className="font-semibold">Username: </span>guest
                      </span>
                      <CopyIcon
                        className="w-4 h-4 cursor-pointer"
                        onClick={() => copyToClipboard("guest")}
                      />
                    </div>
                    <div className="flex justify-between py-2 px-2 bg-muted/50 rounded-md">
                      <span className="text-sm">
                        <span className="font-semibold">Password: </span>
                        guest123
                      </span>
                      <CopyIcon
                        className="w-4 h-4 cursor-pointer"
                        onClick={() => copyToClipboard("guest123")}
                      />
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
            <div
              className="flex flex-col gap-2"
              onKeyDown={(e) => e.key === "Enter" && onSubmit()}
            >
              {fields.map((field) => (
                <CustomField key={field.name} form={form} fieldInfo={field} />
              ))}
            </div>
            <Button type="button" className="cursor-pointer" onClick={onSubmit}>
              Login {isLoading && <Spinner className="size-5" />}
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

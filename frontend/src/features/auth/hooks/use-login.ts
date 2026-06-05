import { useMutation } from "@tanstack/react-query";
import { useRouter, useSearch } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { useAuth } from "@/auth";
import { loginRequest } from "../api";
import { parseLoginError } from "../lib/parse-login-error";
import type { LoginPayload } from "../types";

export function useLogin() {
	const { login } = useAuth();
	const router = useRouter();
	const search = useSearch({ from: "/login" });

	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [showPassword, setShowPassword] = useState(false);

	const mutation = useMutation({
		mutationFn: (payload: LoginPayload) => loginRequest(payload),
		onSuccess: (data) => {
			login(data.payload.access);
			router.navigate({ to: search.redirect ?? "/home", replace: true });
		},
		onError: (error) => {
			toast.error(parseLoginError(error));
		},
	});

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		if (!username.trim() || !password) return;
		mutation.mutate({ username: username.trim(), password });
	};

	return {
		username,
		setUsername,
		password,
		setPassword,
		showPassword,
		setShowPassword,
		isPending: mutation.isPending,
		handleSubmit,
	};
}

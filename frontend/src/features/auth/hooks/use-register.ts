import { useMutation } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { parseApiError } from "@/features/access/lib/parse-error";
import { registerRequest } from "../api";

const MIN_PASSWORD_LENGTH = 6;

export function useRegister(invitationToken: string | undefined) {
	const router = useRouter();

	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [confirm, setConfirm] = useState("");
	const [showPassword, setShowPassword] = useState(false);

	const mutation = useMutation({
		mutationFn: registerRequest,
		onSuccess: () => {
			toast.success("Account created. You can sign in now.");
			router.navigate({ to: "/login", replace: true });
		},
		onError: (error) => {
			toast.error(
				parseApiError(error, "Registration failed. Please try again."),
			);
		},
	});

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		if (!username.trim()) return;
		if (password.length < MIN_PASSWORD_LENGTH) {
			toast.error(
				`Password must be at least ${MIN_PASSWORD_LENGTH} characters`,
			);
			return;
		}
		if (password !== confirm) {
			toast.error("Passwords do not match");
			return;
		}
		mutation.mutate({
			username: username.trim(),
			password,
			invitationToken,
		});
	};

	return {
		username,
		setUsername,
		password,
		setPassword,
		confirm,
		setConfirm,
		showPassword,
		setShowPassword,
		isPending: mutation.isPending,
		handleSubmit,
	};
}

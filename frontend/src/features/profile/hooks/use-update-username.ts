import { useForm } from "@tanstack/react-form";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuth } from "@/auth";
import { updateUserRequest } from "../api";
import { parseUpdateError } from "../lib/parse-update-error";
import { usernameSchema } from "../schemas";

export function useUpdateUsername() {
	const { user, logout } = useAuth();

	const mutation = useMutation({
		mutationFn: updateUserRequest,
		onSuccess: () => {
			toast.success("Username updated. Please sign in again.");
			logout();
		},
		onError: (error) => {
			toast.error(parseUpdateError(error));
		},
	});

	const form = useForm({
		defaultValues: { username: user?.username ?? "" },
		validators: { onChange: usernameSchema },
		onSubmit: async ({ value }) => {
			await mutation.mutateAsync({ username: value.username.trim() });
		},
	});

	return { form, isPending: mutation.isPending };
}

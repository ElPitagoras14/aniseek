import { useForm } from "@tanstack/react-form";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { updateUserRequest } from "../api";
import { parseUpdateError } from "../lib/parse-update-error";
import { passwordSchema } from "../schemas";

export function useUpdatePassword() {
	const mutation = useMutation({
		mutationFn: updateUserRequest,
		onSuccess: () => {
			toast.success("Password updated.");
		},
		onError: (error) => {
			toast.error(parseUpdateError(error));
		},
	});

	const form = useForm({
		defaultValues: {
			currentPassword: "",
			newPassword: "",
			confirmPassword: "",
		},
		validators: { onChange: passwordSchema },
		onSubmit: async ({ value, formApi }) => {
			await mutation.mutateAsync({
				password: {
					currentPassword: value.currentPassword,
					newPassword: value.newPassword,
				},
			});
			formApi.reset();
		},
	});

	return { form, isPending: mutation.isPending };
}

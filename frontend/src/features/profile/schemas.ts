import { z } from "zod";

export const usernameSchema = z.object({
	username: z.string().trim().min(1, "Username is required"),
});

export const passwordSchema = z
	.object({
		currentPassword: z.string().min(1, "Current password is required"),
		newPassword: z.string().min(8, "Must be at least 8 characters"),
		confirmPassword: z.string().min(1, "Please confirm the new password"),
	})
	.refine((v) => v.newPassword === v.confirmPassword, {
		message: "Passwords do not match",
		path: ["confirmPassword"],
	})
	.refine((v) => v.newPassword !== v.currentPassword, {
		message: "New password must differ from the current one",
		path: ["newPassword"],
	});

export interface UpdateUserPayload {
	username?: string;
	password?: { currentPassword: string; newPassword: string };
}

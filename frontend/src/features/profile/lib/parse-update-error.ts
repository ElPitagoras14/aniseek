import axios from "axios";

export function parseUpdateError(error: unknown): string {
	if (axios.isAxiosError(error)) {
		const data = error.response?.data as { message?: string } | undefined;
		if (data?.message) return data.message;
		// backend raises ConflictError (409) when the provided currentPassword does not match
		if (error.response?.status === 409) return "Current password is incorrect";
		if (error.response?.status === 404) return "User not found";
	}
	return "Could not update. Please try again.";
}

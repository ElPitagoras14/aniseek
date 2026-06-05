import axios from "axios";

export function parseLoginError(error: unknown): string {
	if (axios.isAxiosError(error)) {
		const data = error.response?.data as { message?: string } | undefined;
		if (data?.message) return data.message;
		if (error.response?.status === 401) return "Invalid credentials";
		if (error.response?.status === 404) return "User not found";
		if (error.response?.status === 409) return "Invalid credentials";
		if (error.response?.status === 403) return "Account inactive";
	}
	return "Login failed. Please try again.";
}

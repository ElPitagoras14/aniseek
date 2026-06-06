import { api } from "@/api";
import type { UpdateUserPayload } from "./schemas";

export async function updateUserRequest(
	payload: UpdateUserPayload,
): Promise<string> {
	const { data } = await api.put<{ payload: string }>("/users", payload);
	return data.payload;
}

export interface UserProfile {
	createdAt: string;
}

export async function getUserProfile(): Promise<UserProfile> {
	const { data } = await api.get<UserProfile>("/users/me");
	return data;
}

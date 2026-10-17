import { api } from "@/api";
import type { LoginPayload, LoginResponse } from "./types";

export async function loginRequest(
	payload: LoginPayload,
): Promise<LoginResponse> {
	const { data } = await api.post<LoginResponse>("/auth/login", payload);
	return data;
}

export async function registerRequest(payload: {
	username: string;
	password: string;
	invitationToken?: string;
}): Promise<void> {
	await api.post("/auth/register", payload);
}

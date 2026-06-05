import { api } from "@/api";
import type { LoginPayload, LoginResponse } from "./types";

export async function loginRequest(
	payload: LoginPayload,
): Promise<LoginResponse> {
	const { data } = await api.post<LoginResponse>("/auth/login", payload);
	return data;
}

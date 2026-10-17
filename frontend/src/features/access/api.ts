import { queryOptions } from "@tanstack/react-query";
import { api } from "@/api";
import type { ApiEnvelope } from "@/features/anime/types";
import type {
	AccessUser,
	ApiKey,
	CreatedApiKey,
	CreatedInvitation,
	InstanceSettings,
	InvitationList,
	RegistrationPolicy,
	Role,
	UserApiKeyList,
	UserList,
} from "./types";

export const currentUserQueryOptions = queryOptions({
	queryKey: ["users", "me"] as const,
	queryFn: async (): Promise<AccessUser> => {
		const { data } = await api.get<ApiEnvelope<AccessUser>>("/users/me");
		return data.payload;
	},
	staleTime: 60_000,
});

export const usersQueryOptions = queryOptions({
	queryKey: ["users", "list"] as const,
	queryFn: async (): Promise<UserList> => {
		const { data } = await api.get<ApiEnvelope<UserList>>("/users");
		return data.payload;
	},
});

export const invitationsQueryOptions = queryOptions({
	queryKey: ["invitations"] as const,
	queryFn: async (): Promise<InvitationList> => {
		const { data } = await api.get<ApiEnvelope<InvitationList>>("/invitations");
		return data.payload;
	},
});

export const settingsQueryOptions = queryOptions({
	queryKey: ["settings"] as const,
	queryFn: async (): Promise<InstanceSettings> => {
		const { data } = await api.get<ApiEnvelope<InstanceSettings>>("/settings");
		return data.payload;
	},
});

export const registrationPolicyQueryOptions = queryOptions({
	queryKey: ["auth", "registration"] as const,
	queryFn: async (): Promise<RegistrationPolicy> => {
		const { data } =
			await api.get<ApiEnvelope<{ policy: RegistrationPolicy }>>(
				"/auth/registration",
			);
		return data.payload.policy;
	},
	staleTime: 60_000,
});

export async function createUser(payload: {
	username: string;
	password: string;
	role: Role;
}): Promise<AccessUser> {
	const { data } = await api.post<ApiEnvelope<AccessUser>>("/users", payload);
	return data.payload;
}

export async function updateManagedUser(
	userId: string,
	payload: { isActive?: boolean; role?: Role },
): Promise<AccessUser> {
	const { data } = await api.patch<ApiEnvelope<AccessUser>>(
		`/users/${userId}`,
		payload,
	);
	return data.payload;
}

export async function resetUserPassword(
	userId: string,
	password: string,
): Promise<void> {
	await api.put(`/users/${userId}/password`, { password });
}

export async function createInvitation(payload: {
	role: Role;
	expiresInDays: number;
}): Promise<CreatedInvitation> {
	const { data } = await api.post<ApiEnvelope<CreatedInvitation>>(
		"/invitations",
		payload,
	);
	return data.payload;
}

export async function revokeInvitation(id: string): Promise<void> {
	await api.delete(`/invitations/${id}`);
}

export async function updateRegistrationPolicy(
	registrationPolicy: RegistrationPolicy,
): Promise<void> {
	await api.put("/settings", { registrationPolicy });
}

// Any user: whether agents can connect to this instance.
export const mcpStatusQueryOptions = queryOptions({
	queryKey: ["settings", "mcp"] as const,
	queryFn: async (): Promise<{ enabled: boolean }> => {
		const { data } =
			await api.get<ApiEnvelope<{ enabled: boolean }>>("/settings/mcp");
		return data.payload;
	},
});

// Owner only.
export async function updateMcpEnabled(enabled: boolean): Promise<void> {
	await api.put("/settings/mcp", { enabled });
}

export const ownApiKeyQueryOptions = queryOptions({
	queryKey: ["api-keys", "me"] as const,
	queryFn: async (): Promise<ApiKey | null> => {
		const { data } = await api.get<ApiEnvelope<ApiKey | null>>("/api-keys/me");
		return data.payload;
	},
});

// Owner only.
export const apiKeysQueryOptions = queryOptions({
	queryKey: ["api-keys", "list"] as const,
	queryFn: async (): Promise<UserApiKeyList> => {
		const { data } = await api.get<ApiEnvelope<UserApiKeyList>>("/api-keys");
		return data.payload;
	},
});

// Generates the key, or replaces the current one.
export async function generateApiKey(): Promise<CreatedApiKey> {
	const { data } = await api.post<ApiEnvelope<CreatedApiKey>>("/api-keys/me");
	return data.payload;
}

export async function revokeOwnApiKey(): Promise<void> {
	await api.delete("/api-keys/me");
}

export async function revokeUserApiKey(userId: string): Promise<void> {
	await api.delete(`/api-keys/${userId}`);
}

export async function transferOwner(payload: {
	targetUserId: string;
	currentPassword: string;
}): Promise<void> {
	await api.post("/owner/transfer", payload);
}

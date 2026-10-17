export type Role = "owner" | "admin" | "member";

export interface AccessUser {
	id: string;
	username: string;
	avatarUrl: string | null;
	avatarLabel: string | null;
	role: Role;
	isActive: boolean;
	createdAt: string | null;
	updatedAt: string | null;
}

export interface UserList {
	items: AccessUser[];
	total: number;
}

export type RegistrationPolicy = "invite" | "open";

export interface Invitation {
	id: string;
	role: Role;
	createdAt: string;
	expiresAt: string;
	createdBy: string | null;
	// Only set once the invitation has been used.
	usedAt: string | null;
	usedBy: string | null;
}

export interface InvitationList {
	items: Invitation[];
	total: number;
}

export interface CreatedInvitation {
	id: string;
	token: string;
	role: Role;
	expiresAt: string;
}

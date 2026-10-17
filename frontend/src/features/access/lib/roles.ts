import type { Role } from "../types";

// Mirror of the backend hierarchy (member < admin < owner). The UI only uses
// it to show or hide things: the backend is what enforces.
const RANK: Record<Role, number> = { member: 0, admin: 1, owner: 2 };

export const ROLE_LABELS: Record<string, string> = {
	owner: "Owner",
	admin: "Administrator",
	member: "Member",
};

export function hasRole(role: string | undefined, min: Role): boolean {
	if (!role || !(role in RANK)) return false;
	return RANK[role as Role] >= RANK[min];
}

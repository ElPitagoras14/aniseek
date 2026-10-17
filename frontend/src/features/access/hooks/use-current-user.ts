import { useQuery } from "@tanstack/react-query";
import { currentUserQueryOptions } from "../api";
import { hasRole } from "../lib/roles";
import type { Role } from "../types";

// The role comes from GET /users/me, not from the JWT: the token's role can
// be stale after a role change. Works in single-user mode too, where the
// backend resolves every request as the owner.
export function useCurrentUser() {
	return useQuery(currentUserQueryOptions);
}

// False while the user is loading, so restricted actions never flash.
export function useHasRole(min: Role): boolean {
	const { data } = useCurrentUser();
	return hasRole(data?.role, min);
}

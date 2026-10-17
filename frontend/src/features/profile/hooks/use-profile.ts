import { useCurrentUser } from "@/features/access/hooks/use-current-user";

export function useProfile() {
	return useCurrentUser();
}

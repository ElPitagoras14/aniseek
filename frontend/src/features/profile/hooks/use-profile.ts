import { useQuery } from "@tanstack/react-query";
import { getUserProfile } from "../api";

export function useProfile() {
	return useQuery({
		queryKey: ["profile"],
		queryFn: getUserProfile,
	});
}

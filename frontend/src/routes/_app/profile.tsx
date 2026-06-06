import { createFileRoute } from "@tanstack/react-router";
import { ProfilePage } from "@/features/profile/components/profile-page";

export const Route = createFileRoute("/_app/profile")({
	component: ProfilePage,
});

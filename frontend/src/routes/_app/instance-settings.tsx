import { createFileRoute } from "@tanstack/react-router";
import { SettingsPage } from "@/features/settings/components/settings-page";

export const Route = createFileRoute("/_app/instance-settings")({
	component: SettingsPage,
});

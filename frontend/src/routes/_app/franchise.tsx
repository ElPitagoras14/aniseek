import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_app/franchise")({
	component: RouteComponent,
});

function RouteComponent() {
	return <div>Hello "/_app/franchise"!</div>;
}

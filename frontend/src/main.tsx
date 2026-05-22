// NetworkHub frontend — v0.1.7
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createRouter, RouterProvider } from "@tanstack/react-router";
import React from "react";
import ReactDOM from "react-dom/client";
import { AuthProvider, useAuth } from "./auth";
import { routeTree } from "./routeTree.gen";
import "./styles.css";

const queryClient = new QueryClient();

const router = createRouter({
	routeTree,
	defaultPreload: "intent",
	scrollRestoration: true,
	context: {
		// biome-ignore lint/style/noNonNullAssertion: Tanstack Router requires this to be non-null
		auth: undefined!,
	},
});

declare module "@tanstack/react-router" {
	interface Register {
		router: typeof router;
	}
}

function InnerApp() {
	const auth = useAuth();
	return <RouterProvider router={router} context={{ auth }} />;
}

function App() {
	return (
		<AuthProvider>
			<QueryClientProvider client={queryClient}>
				<InnerApp />
			</QueryClientProvider>
		</AuthProvider>
	);
}

const rootElement = document.getElementById("app");

if (!rootElement) {
	throw new Error("Could not find root element");
}

if (!rootElement.innerHTML) {
	const root = ReactDOM.createRoot(rootElement);
	root.render(
		<React.StrictMode>
			<App />
		</React.StrictMode>,
	);
}

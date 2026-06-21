import { readFileSync } from "node:fs";
import tailwindcss from "@tailwindcss/vite";
import { devtools } from "@tanstack/devtools-vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import viteReact from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";
import { VitePWA } from "vite-plugin-pwa";

const { version } = JSON.parse(readFileSync("./package.json", "utf-8"));

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, "..", "");
	return {
		envDir: "..",
		define: {
			__APP_VERSION__: JSON.stringify(version),
			__API_URL__: JSON.stringify(env.API_URL),
			__AUTH_ENABLED__: JSON.stringify(env.AUTH_ENABLED),
		},
		resolve: { tsconfigPaths: true },
		server: {
			port: 3000,
			proxy: {
				"/api": {
					target: "http://localhost:8000",
					changeOrigin: true,
				},
			},
		},
		plugins: [
			devtools(),
			tailwindcss(),
			tanstackRouter({ target: "react", autoCodeSplitting: true }),
			viteReact(),
			VitePWA({
				registerType: "autoUpdate",
				manifest: false,
				workbox: {
					clientsClaim: true,
					skipWaiting: true,
				},
				devOptions: {
					enabled: true,
				},
			}),
		],
	};
});

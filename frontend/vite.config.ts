import { readFileSync } from "node:fs";
import tailwindcss from "@tailwindcss/vite";
import { devtools } from "@tanstack/devtools-vite";

import { tanstackRouter } from "@tanstack/router-plugin/vite";

import viteReact from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const { version } = JSON.parse(readFileSync("./package.json", "utf-8"));

const config = defineConfig({
	envDir: "..",
	define: {
		__APP_VERSION__: JSON.stringify(version),
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
	],
});

export default config;

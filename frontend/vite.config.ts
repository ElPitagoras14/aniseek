import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import { devtools } from "@tanstack/devtools-vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import viteReact from "@vitejs/plugin-react";
import { defineConfig, loadEnv, type Plugin } from "vite";

const ENV_DIR = "..";

// Sirve /config.js en desarrollo igual que entrypoint.sh lo escribe en el
// container: sustituyendo config.template.js con las variables del .env de
// la raíz. No depende de envsubst (no disponible en Windows) y relee el
// .env en cada request, para que cambiarlo y recargar la página alcance.
function runtimeConfigPlugin(mode: string): Plugin {
	const templatePath = fileURLToPath(
		new URL("./config.template.js", import.meta.url),
	);

	// Falla al arrancar el servidor de desarrollo, no en silencio en la
	// primera request, si la plantilla no se puede leer.
	let template: string;
	try {
		template = readFileSync(templatePath, "utf-8");
	} catch (error) {
		throw new Error(
			`runtime-config: no se pudo leer la plantilla en ${templatePath}: ${(error as Error).message}`,
		);
	}

	return {
		name: "runtime-config",
		configureServer(server) {
			server.middlewares.use((req, res, next) => {
				if (req.url !== "/config.js") {
					next();
					return;
				}
				// Mismo comportamiento que envsubst: una variable ausente del
				// .env se sustituye por cadena vacía, no se deja el ${VAR}
				// literal ni se omite la clave.
				const env = loadEnv(mode, ENV_DIR, "");
				const rendered = template.replace(
					/\$\{(\w+)\}/g,
					(_match, key) => env[key] ?? "",
				);
				res.setHeader("Content-Type", "text/javascript");
				res.end(rendered);
			});
		},
	};
}

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, ENV_DIR, "");
	return {
		envDir: ENV_DIR,
		define: {
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
			runtimeConfigPlugin(mode),
			devtools(),
			tailwindcss(),
			tanstackRouter({ target: "react", autoCodeSplitting: true }),
			viteReact(),
		],
		build: {
			rolldownOptions: {
				output: {
					manualChunks: (id) => {
						if (id.includes("/react/") || id.includes("/react-dom/"))
							return "vendor-react";
						if (id.includes("/@tanstack/")) return "vendor-tanstack";
						if (id.includes("/radix-ui/")) return "vendor-radix";
						if (
							id.includes("/lucide-react/") ||
							id.includes("/sonner/") ||
							id.includes("/next-themes/") ||
							id.includes("/clsx/") ||
							id.includes("/tailwind-merge/") ||
							id.includes("/class-variance-authority/")
						)
							return "vendor-ui";
					},
				},
			},
		},
	};
});

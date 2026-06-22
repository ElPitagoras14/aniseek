export const config: AppConfig | undefined = window.__APP_CONFIG__;

declare const __API_URL__: string | undefined;
declare const __AUTH_ENABLED__: string | undefined;

export const apiUrl: string =
	config?.API_URL !== undefined
		? config.API_URL
		: typeof __API_URL__ !== "undefined"
			? __API_URL__
			: "";

export const isAuthEnabled: boolean =
	config?.AUTH_ENABLED !== undefined
		? config.AUTH_ENABLED === true ||
		  String(config.AUTH_ENABLED).toLowerCase() === "true"
		: typeof __AUTH_ENABLED__ !== "undefined"
			? __AUTH_ENABLED__.toLowerCase() === "true"
			: false;

export const config: AppConfig = window.__APP_CONFIG__;

declare const __API_URL__: string | undefined;
declare const __AUTH_ENABLED__: string | undefined;

export const apiUrl: string =
	typeof __API_URL__ !== "undefined" ? __API_URL__ : config.API_URL;

export const isAuthEnabled: boolean =
	typeof __AUTH_ENABLED__ !== "undefined"
		? __AUTH_ENABLED__ === "true"
		: config.AUTH_ENABLED === true || config.AUTH_ENABLED === "true";

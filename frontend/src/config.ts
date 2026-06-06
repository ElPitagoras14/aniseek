export const config: AppConfig = window.__APP_CONFIG__;

export const isAuthEnabled: boolean =
	config.AUTH_ENABLED === true || config.AUTH_ENABLED === "true";

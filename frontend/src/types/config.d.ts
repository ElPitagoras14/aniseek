declare global {
	const __APP_VERSION__: string;
	interface AppConfig {
		API_URL: string;
		AUTH_ENABLED: string | boolean;
	}
	interface Window {
		__APP_CONFIG__: AppConfig;
	}
}

export {};

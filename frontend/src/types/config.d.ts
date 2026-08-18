declare global {
	interface AppConfig {
		API_URL: string;
		AUTH_ENABLED: string | boolean;
		APP_VERSION: string;
	}
	interface Window {
		__APP_CONFIG__: AppConfig;
	}
}

export {};

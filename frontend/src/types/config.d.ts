declare global {
	interface AppConfig {
		API_URL: string;
		AUTH_ENABLED: string;
	}
	interface Window {
		__APP_CONFIG__: AppConfig;
	}
}

export {};

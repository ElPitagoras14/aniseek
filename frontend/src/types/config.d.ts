interface AppConfig {
	API_URL: string;
}

declare global {
	interface Window {
		__APP_CONFIG__: AppConfig;
	}
}

export {};

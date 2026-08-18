export const config: AppConfig | undefined = window.__APP_CONFIG__;

declare const __API_URL__: string | undefined;
declare const __AUTH_ENABLED__: string | undefined;

/**
 * Parsea un valor crudo de una capa de configuración. Devuelve `undefined`
 * cuando ese valor cuenta como "no configurado" para la clave — lo que hace
 * que `resolve` siga probando la capa siguiente.
 */
type Parser<T> = (raw: unknown) => T | undefined;

/**
 * Precedencia runtime → build-time → default, escrita una sola vez. Para
 * cada candidato, en orden, se aplica `parse`; el primero que resuelva a un
 * valor definido gana. Si ninguno lo hace, se usa `defaultValue`.
 */
function resolve<T>(
	candidates: unknown[],
	parse: Parser<T>,
	defaultValue: T,
): T {
	for (const candidate of candidates) {
		const parsed = parse(candidate);
		if (parsed !== undefined) return parsed;
	}
	return defaultValue;
}

// API_URL: cualquier string es un valor configurado, incluida la cadena
// vacía — significa "mismo origen", proxeado por nginx en producción y por
// el `server.proxy` de Vite en desarrollo.
const parseApiUrl: Parser<string> = (raw) =>
	typeof raw === "string" ? raw : undefined;

// AUTH_ENABLED: solo "true"/"false" (sin distinguir mayúsculas) cuentan como
// configurado. La cadena vacía —lo que escribe envsubst para una variable
// ausente— y cualquier otro valor cuentan como ausencia, no como "false".
const parseAuthEnabled: Parser<boolean> = (raw) => {
	if (typeof raw === "boolean") return raw;
	if (typeof raw !== "string" || raw === "") return undefined;
	const normalized = raw.toLowerCase();
	if (normalized === "true") return true;
	if (normalized === "false") return false;
	return undefined;
};

export const apiUrl: string = resolve(
	[config?.API_URL, __API_URL__],
	parseApiUrl,
	"",
);

// Default final: habilitada. Una configuración ausente falla cerrada, igual
// que el backend (`AuthSettings.AUTH_ENABLED` default `True`).
export const isAuthEnabled: boolean = resolve(
	[config?.AUTH_ENABLED, __AUTH_ENABLED__],
	parseAuthEnabled,
	true,
);

// APP_VERSION: cualquier string no vacío cuenta como configurado. La cadena
// vacía —lo que escribe envsubst para una variable ausente— cuenta como
// ausencia, para que la interfaz no aparente un release que no existe.
const parseAppVersion: Parser<string> = (raw) =>
	typeof raw === "string" && raw !== "" ? raw : undefined;

// Sin capa de build-time: la imagen siempre trae el archivo, y en desarrollo
// la clave se resuelve por el `.env` de la raíz o cae al default.
export const appVersion: string = resolve(
	[config?.APP_VERSION],
	parseAppVersion,
	"dev",
);

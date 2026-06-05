# Página de login

> Vamos a crear una página de login para para iniciar sesión en la web. Quiero algo similar a la imagen de referencia, que sea responsive. use feature-spec

Archivo principal: `frontend/src/routes/login.tsx`

## Restricciones

- Frontend-only: el endpoint `POST /api/auth/login` ya existe en el backend, no se modifica código Python ni SQL.
- Sin dependencias nuevas en `package.json`.
- Sin comentarios en el código.
- Usar componentes shadcn/ui del proyecto (`Card`, `Input`, `Button`, `Separator`, `Label`).
- Tema dark por defecto (la imagen de referencia es dark; `index.html` ya tiene `class="dark"`).
- Responsive: mobile (`<sm`), tablet (`sm-md`), desktop (`md+`).
- Path aliases: `@/components`, `@/lib`, `@/features`, `@/hooks`.
- Formato Biome (tabs, double quotes en JS).
- Sin `any`; `interface` para props; imports ordenados stdlib → third-party → local.
- No incluir dropdown de "Guest User" (la imagen lo mostraba, pero el usuario pidió eliminarlo porque se usarán usuarios reales).
- Para el auto-login de dev (`AUTH_ENABLED=false`) usar credenciales **hardcodeadas** `admin` / `admin123` (es uso personal, no público).
- Footer con URLs **hardcodeadas** a `https://github.com/ElPitagoras14/aniseek` y `https://buymeacoffee.com/jhonyg`.

## Vista

Pantalla `/login` con fondo `bg-background`, contenido centrado vertical y horizontalmente. Un único `Card` con tres secciones separadas por `Separator`: header, form y footer.

### A · Header

Icono decorativo + título + subtítulo + link "Sign up".

- Icono `Clapperboard` (lucide) `size-10 text-muted-foreground`.
- `h1` "Welcome to Ani Seek" con `text-2xl font-bold tracking-tight`.
- `p` "A simple way to scrap anime" con `text-sm text-muted-foreground`.
- Línea de CTA: texto `Don't have an account?` + `<Link to="/register" className="text-primary underline-offset-4 hover:underline">Sign up</Link>`.
- Layout: `flex flex-col items-center gap-2 text-center`.

### B · Form

Form controlado por el hook `useLogin()` con dos inputs y un botón.

- `Label` + `Input` para `username` con `autoComplete="username"`, `name="username"`, `required`, `placeholder="Username"`.
- `Label` + `Input` para `password` con `type={showPassword ? "text" : "password"}`, `autoComplete="current-password"`, `name="password"`, `required`. Wrapper relativo con botón absoluto a la derecha que alterna `Eye` / `EyeOff` (lucide).
- `Button type="submit"` full width, texto "Login", `disabled={isPending}`. Cuando `isPending` muestra `Loader2Icon animate-spin` a la izquierda del texto.
- Layout: `flex flex-col gap-4` dentro de un `<form onSubmit={handleSubmit}>`.

### C · Footer

Dos enlaces externos separados por `Separator orientation="vertical"`.

- `<a href="https://github.com/ElPitagoras14/aniseek" target="_blank" rel="noreferrer">` con `Github` icon + texto "Github".
- `Separator orientation="vertical" className="h-4"`.
- `<a href="https://buymeacoffee.com/jhonyg" target="_blank" rel="noreferrer">` con `Coffee` icon + texto "Support it".
- Layout: `flex items-center justify-center gap-3 text-sm text-muted-foreground`.

## Layout responsive

| Breakpoint | Comportamiento |
|---|---|
| `< sm` (< 640px) | Card `w-full`, padding `p-4`, footer horizontal (sin wrap) |
| `sm` (≥ 640px) | Card `max-w-sm`, `mx-auto` |
| `md+` (≥ 768px) | Card `max-w-md`, `mx-auto` |

Wrapper de la página: `min-h-svh flex items-center justify-center p-4`.

## General

### Endpoint a consumir

`POST /api/auth/login` (existente, sin cambios backend).

**Request:**

```json
{ "username": "string", "password": "string" }
```

**Response 200:**

```json
{
  "status": "success",
  "message": "User logged in successfully",
  "payload": { "access": "<jwt>", "refresh": "<jwt>" },
  "statusCode": 200
}
```

**Response 404** (`NotFoundError`): `{ "status": "error", "message": "User not found", "statusCode": 404 }`

**Response 409** (`ConflictError`): `{ "status": "error", "message": "Password is wrong" | "User is not active", "statusCode": 409 }`

El JWT trae los claims `id, username, isActive, role, avatarUrl, avatarLabel`. `useAuth().login(token)` ya decodifica el payload y popula `user` con `{ username, role }`.

### Sin cambios en backend

No se modifican archivos de `backend/`. El endpoint ya existe y devuelve la estructura esperada.

## Flag `AUTH_ENABLED`

Nuevo flag de runtime leído desde `window.__APP_CONFIG__.AUTH_ENABLED` (string `"true"` o `"false"`, inyectado por `envsubst` en `entrypoint.sh` desde la variable de entorno `AUTH_ENABLED` que ya se pasa al backend en `compose.yaml`).

| `AUTH_ENABLED` | Visitante en `/login` (no auth) | Visitante en `/_app/*` (no auth) | Autenticado en `/login` | Autenticado en `/_app/*` |
|---|---|---|---|---|
| `false` | Auto-login con `admin`/`admin123` → `/home` | Auto-login con `admin`/`admin123` (dev) | Redirect a `/home` | Acceso directo |
| `true` | Muestra form | Redirect a `/login?redirect=…` | Redirect a `?redirect=` o `/home` | Acceso directo |

Nota: `compose.yaml` **no se modifica** en este spec. El frontend lee `AUTH_ENABLED` desde su propio servicio, pero como el contenedor de nginx ejecuta `envsubst` sobre `config.template.js`, basta con añadir la variable al template y a la interfaz TS; el operador puede definirla en su `.env` (la variable ya existe para el backend).

## Estructura de archivos

### Crear (9)

- `frontend/src/features/auth/api.ts` — `loginRequest(payload)` que llama `api.post<LoginResponse>("/auth/login", payload)` y devuelve la respuesta.
- `frontend/src/features/auth/types.ts` — interfaces `LoginPayload`, `LoginResponse`.
- `frontend/src/features/auth/hooks/use-login.ts` — hook con state de form (`username`, `password`, `showPassword`), `useMutation`, `handleSubmit`, navegación a `?redirect=` o `/home` en éxito, toast en error.
- `frontend/src/features/auth/lib/parse-login-error.ts` — `parseLoginError(error: unknown): string` que mapea `AxiosError` a mensaje legible.
- `frontend/src/features/auth/components/login-card.tsx` — orquestador del `Card` con `LoginHeader`, `Separator`, `LoginForm`, `Separator`, `LoginFooter`.
- `frontend/src/features/auth/components/login-header.tsx` — icono + título + subtítulo + link "Sign up".
- `frontend/src/features/auth/components/login-form.tsx` — form con username/password/show-hide/submit.
- `frontend/src/features/auth/components/login-footer.tsx` — enlaces Github y Buy Me a Coffee.
- `frontend/src/routes/register.tsx` — stub (`<div>Hello "/register"!</div>`) listo para el spec de registro.

### Modificar (5)

- `frontend/src/routes/login.tsx` — reemplazar stub por `RouteComponent` que renderiza `<LoginCard />`. Añadir `validateSearch` con `redirect?: string`. `beforeLoad`: si `!isAuthEnabled`, ejecutar auto-login con `admin`/`admin123` y `throw redirect({ to: "/home" })`; si `isAuthEnabled && context.auth.isAuthenticated`, `throw redirect({ to: search.redirect ?? "/home" })`.
- `frontend/src/routes/_app/route.tsx` — el guard actual hace auto-login hardcodeado siempre. Cambiar para que:
  - Si `!isAuthEnabled`: comportamiento actual (auto-login con `admin`/`admin123`).
  - Si `isAuthEnabled && !context.auth.isAuthenticated`: `throw redirect({ to: "/login", search: { redirect: location.href } })`.
- `frontend/public/config.template.js` — añadir `AUTH_ENABLED: "${AUTH_ENABLED}"` al objeto `window.__APP_CONFIG__`.
- `frontend/src/types/config.d.ts` — añadir `AUTH_ENABLED: string` a `interface AppConfig` (queda como string; la coerción a boolean vive en `config.ts`).
- `frontend/src/config.ts` — añadir `export const isAuthEnabled: boolean = config.AUTH_ENABLED === "true"`.

### NO se modifican

- `backend/**` — sin cambios.
- `postgres/init.sql` — sin cambios.
- `compose.yaml` — sin cambios.
- `Dockerfile`, `entrypoint.sh`, `nginx.conf` — sin cambios.
- `package.json` — sin nuevas dependencias.

## Utilidades

### `features/auth/api.ts`

```ts
import { api } from "@/api";
import type { LoginPayload, LoginResponse } from "./types";

export async function loginRequest(payload: LoginPayload): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>("/auth/login", payload);
  return data;
}
```

### `features/auth/lib/parse-login-error.ts`

```ts
import axios from "axios";

export function parseLoginError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { message?: string } | undefined;
    if (data?.message) return data.message;
    if (error.response?.status === 401) return "Invalid credentials";
    if (error.response?.status === 404) return "User not found";
    if (error.response?.status === 409) return "Invalid credentials";
    if (error.response?.status === 403) return "Account inactive";
  }
  return "Login failed. Please try again.";
}
```

### `features/auth/hooks/use-login.ts`

```ts
import { useMutation } from "@tanstack/react-query";
import { useRouter, useSearch } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { useAuth } from "@/auth";
import { loginRequest } from "../api";
import { parseLoginError } from "../lib/parse-login-error";
import type { LoginPayload } from "../types";

export function useLogin() {
  const { login } = useAuth();
  const router = useRouter();
  const search = useSearch({ from: "/login" });

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const mutation = useMutation({
    mutationFn: (payload: LoginPayload) => loginRequest(payload),
    onSuccess: (data) => {
      login(data.payload.access);
      router.navigate({ to: search.redirect ?? "/home", replace: true });
    },
    onError: (error) => {
      toast.error(parseLoginError(error));
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) return;
    mutation.mutate({ username: username.trim(), password });
  };

  return {
    username,
    setUsername,
    password,
    setPassword,
    showPassword,
    setShowPassword,
    isPending: mutation.isPending,
    handleSubmit,
  };
}
```

## Query keys / data fetching

No hay queries de lectura. La única operación es una mutation:

| Operación | Wrapper | Endpoint | onSuccess | onError |
|---|---|---|---|---|
| `useLogin` | `useMutation` | `POST /api/auth/login` | `auth.login(access) + navigate(redirect ?? "/home")` | `toast.error(parseLoginError(e))` |

Invalidación de queries tras login exitoso: no requerida (las queries en `/_app/*` se ejecutan en mount de cada ruta; TanStack Query ya maneja el refetch). Si en el futuro se necesita refrescar queries globales al volver de un logout/login, se documenta en otro spec.

## Tipos

### `features/auth/types.ts`

```ts
export interface LoginPayload {
  username: string;
  password: string;
}

export interface LoginResponse {
  status: string;
  message: string;
  payload: { access: string; refresh: string };
  statusCode: number;
}
```

### `types/config.d.ts` (modificado)

```ts
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
```

## Patrones a respetar

- Componentes en `features/auth/components/`, no en `routes/`.
- Hooks en `features/auth/hooks/`.
- Tipos en `features/auth/types.ts`.
- Sin `any`; `interface` para props; `cn()` para combinar clases.
- Imports ordenados: stdlib → third-party (`@/...`) → local (`./...`).
- Biome: tabs, double quotes en JS.
- Sin comentarios en código.
- Formato de errores con `toast.error` de `sonner`.
- Loading con `Loader2Icon animate-spin` (lucide) en el botón submit.
- Accesibilidad: `<Label htmlFor="...">` asociado a cada `Input` con `id` correspondiente; `autoComplete` correcto en cada input.
- `<a>` externos con `target="_blank" rel="noreferrer"`.
- El `Card` se importa de `@/components/ui/card` (existe en el proyecto).
- Para auto-login en dev (`AUTH_ENABLED=false`), las credenciales van **hardcodeadas** como strings literales (`"admin"`, `"admin123"`), nunca desde `.env` ni desde `window.__APP_CONFIG__`.

## Criterios de aceptación

1. `/login` renderiza un `Card` centrado con icono `Clapperboard`, título "Welcome to Ani Seek", subtítulo "A simple way to scrap anime", y link "Sign up" que apunta a `/register`.
2. La pantalla **no** muestra el dropdown "Guest User" de la imagen de referencia.
3. El form tiene `Input` para username (`autoComplete="username"`) y `Input` para password con botón toggle de show/hide.
4. El botón "Login" está full width y muestra `Loader2Icon` durante `isPending`.
5. Submit llama `POST /api/auth/login` con `{ username, password }`. En éxito: `auth.login(data.payload.access)` + navegación a `?redirect=` o `/home` con `replace: true`.
6. En error se muestra `toast.error` con el `message` del backend o un fallback legible.
7. Footer con dos enlaces: `https://github.com/ElPitagoras14/aniseek` (icono `Github`) y `https://buymeacoffee.com/jhonyg` (icono `Coffee`). Ambos con `target="_blank" rel="noreferrer"`.
8. Responsive: mobile full-width, tablet/desktop con `max-w-sm` o `max-w-md` centrado.
9. Tema dark por defecto (sin selector de tema en esta pantalla).
10. Cuando `AUTH_ENABLED=false`:
    - Visitar `/login` ejecuta auto-login con `admin`/`admin123` hardcodeados y redirige a `/home`.
    - Visitar `/_app/*` ejecuta auto-login con `admin`/`admin123` hardcodeados antes de cargar la ruta.
11. Cuando `AUTH_ENABLED=true`:
    - Visitar `/_app/*` sin auth redirige a `/login?redirect=...`.
    - Visitar `/login` autenticado redirige a `?redirect=` o `/home`.
    - Visitar `/login` sin auth muestra el form.
12. `frontend/src/routes/register.tsx` existe como stub (`<div>Hello "/register"!</div>`).
13. `pnpm exec biome check` sin errores nuevos.
14. `pnpm exec tsc --noEmit` sin errores nuevos.
15. `package.json` sin nuevas dependencias.
16. Ningún archivo bajo `backend/`, `postgres/`, `compose.yaml`, `Dockerfile`, `entrypoint.sh`, `nginx.conf` modificado.

Escribir los resultados en este documento

## Resultados

**Fecha de ejecución:** 2026-06-05
**Plan:** `tasks/15-login-page-parallel.md`

### Archivos creados
| Archivo | UoW | Notas |
|---------|-----|-------|
| `frontend/src/features/auth/types.ts` | U1 | `LoginPayload`, `LoginResponse` |
| `frontend/src/features/auth/lib/parse-login-error.ts` | U2 | mapper de AxiosError a mensaje legible |
| `frontend/src/features/auth/api.ts` | U5 | `loginRequest(payload)` |
| `frontend/src/features/auth/hooks/use-login.ts` | U6 | mutation hook con state + redirect + toast |
| `frontend/src/features/auth/components/login-header.tsx` | U8 | icono + título + subtítulo + link "Sign up" |
| `frontend/src/features/auth/components/login-footer.tsx` | U9 | enlaces Github + Buy Me a Coffee |
| `frontend/src/features/auth/components/login-form.tsx` | U10 | form con show/hide + submit |
| `frontend/src/features/auth/components/login-card.tsx` | U11 | orquestador Card + responsive wrapper |
| `frontend/src/components/ui/label.tsx` | U10 | shadcn `Label` (faltaba en el proyecto) |
| `frontend/src/routes/register.tsx` | U12 | stub `<div>Hello "/register"!</div>` |

### Archivos modificados
| Archivo | UoW | Cambio |
|---------|-----|--------|
| `frontend/src/types/config.d.ts` | U3 | añade `AUTH_ENABLED: string` a `AppConfig` |
| `frontend/public/config.template.js` | U4 | añade `AUTH_ENABLED: "${AUTH_ENABLED}"` |
| `frontend/src/config.ts` | U7 | exporta `isAuthEnabled: boolean` |
| `frontend/src/routes/_app/route.tsx` | U13 | gate por `isAuthEnabled` en `beforeLoad` |
| `frontend/src/routes/login.tsx` | U14 | orchestrator: `validateSearch(redirect)` + auto-login + `<LoginCard />` |

### Lint / typecheck
- frontend (biome): ✅
- frontend (tsc --noEmit): ✅

### Notas
- `_app/route.tsx` requirió `biome format --write` para normalizar CRLF→LF y organizar imports; cambios puramente de formato.
- `useLogin()` lee `search.redirect` desde `useSearch({ from: "/login" })`; el tipado del param se materializa cuando U14 declara `validateSearch: z.object({ redirect: z.string().optional() })`.

### Commits
- <none, awaiting user request>

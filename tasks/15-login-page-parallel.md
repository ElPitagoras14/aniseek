# Parallelization plan for tasks/14-login-page

> Source spec: `tasks/14-login-page.md`
> Validation: ✅ 6/6
> Total UoWs: 14
> Waves: 5 (max parallelism 4)

## Units of work

### U1: features/auth/types.ts (login types)
- **Wave**: 1
- **Owns**: `frontend/src/features/auth/types.ts` (create)
- **Reads**: [`frontend/src/features/anime/types.ts:33` (ApiEnvelope shape)]
- **Depends on**: none
- **Spec excerpt**:
  > `features/auth/types.ts` — interfaces `LoginPayload`, `LoginResponse`.
  > ```ts
  > export interface LoginPayload { username: string; password: string; }
  > export interface LoginResponse { status: string; message: string; payload: { access: string; refresh: string }; statusCode: number; }
  > ```
- **Acceptance criteria**:
  1. Exports `LoginPayload` and `LoginResponse` matching the spec shapes.
  2. No imports outside `@/features/auth/...` or the local file.
- **Subagent prompt**:
  ```
  Eres el subagente U1 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (creates):
  - frontend/src/features/auth/types.ts

  NOT_TOUCH (blacklist):
  - any other file under frontend/, backend/, worker/

  READS (consult before writing):
  - frontend/src/features/anime/types.ts (reference: how `ApiEnvelope<T>` is shaped; U1 only needs the literal LoginResponse shape from the spec, not ApiEnvelope)
  - AGENTS.md (project conventions)

  Spec excerpt (verbatim from `tasks/14-login-page.md`):
  > `features/auth/types.ts` — interfaces `LoginPayload`, `LoginResponse`.
  > ```ts
  > export interface LoginPayload {
  >   username: string;
  >   password: string;
  > }
  >
  > export interface LoginResponse {
  >   status: string;
  >   message: string;
  >   payload: { access: string; refresh: string };
  >   statusCode: number;
  > }
  > ```

  Conventions:
  - TypeScript: explicit types, no `any`, no comments.
  - Imports order: stdlib → third-party → local, alphabetical.
  - Biome formatting (tabs, double quotes in JS).

  Acceptance criteria:
  1. Exports `LoginPayload` and `LoginResponse` matching the spec shapes.
  2. No imports outside `@/features/auth/...` or the local file.

  Report back:
  - Files created (full paths)
  - Any deviation from the spec and why
  - Any blocker you could not resolve
  ```

### U2: features/auth/lib/parse-login-error.ts (error mapper)
- **Wave**: 1
- **Owns**: `frontend/src/features/auth/lib/parse-login-error.ts` (create)
- **Reads**: [axios usage in `frontend/src/api.ts`]
- **Depends on**: none
- **Spec excerpt**:
  > `features/auth/lib/parse-login-error.ts` — `parseLoginError(error: unknown): string` que mapea `AxiosError` a mensaje legible.
  > ```ts
  > import axios from "axios";
  > export function parseLoginError(error: unknown): string {
  >   if (axios.isAxiosError(error)) {
  >     const data = error.response?.data as { message?: string } | undefined;
  >     if (data?.message) return data.message;
  >     if (error.response?.status === 401) return "Invalid credentials";
  >     if (error.response?.status === 404) return "User not found";
  >     if (error.response?.status === 409) return "Invalid credentials";
  >     if (error.response?.status === 403) return "Account inactive";
  >   }
  >   return "Login failed. Please try again.";
  > }
  > ```
- **Acceptance criteria**:
  1. Exports `parseLoginError` with the verbatim implementation from the spec.
  2. No `any` (use `unknown` for input).
- **Subagent prompt**:
  ```
  Eres el subagente U2 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (creates):
  - frontend/src/features/auth/lib/parse-login-error.ts

  NOT_TOUCH:
  - any other file under frontend/, backend/, worker/

  READS:
  - frontend/src/api.ts (axios usage pattern)
  - AGENTS.md

  Spec excerpt (verbatim):
  > `features/auth/lib/parse-login-error.ts` — `parseLoginError(error: unknown): string` que mapea `AxiosError` a mensaje legible.
  > ```ts
  > import axios from "axios";
  > export function parseLoginError(error: unknown): string {
  >   if (axios.isAxiosError(error)) {
  >     const data = error.response?.data as { message?: string } | undefined;
  >     if (data?.message) return data.message;
  >     if (error.response?.status === 401) return "Invalid credentials";
  >     if (error.response?.status === 404) return "User not found";
  >     if (error.response?.status === 409) return "Invalid credentials";
  >     if (error.response?.status === 403) return "Account inactive";
  >   }
  >   return "Login failed. Please try again.";
  > }
  > ```

  Conventions:
  - TypeScript: explicit types, no `any` (use `unknown`).
  - Biome formatting (tabs, double quotes).

  Acceptance criteria:
  1. Exports `parseLoginError` matching the spec.
  2. Single function, no extra exports.

  Report back:
  - Files created
  - Any deviation
  - Any blocker
  ```

### U3: types/config.d.ts (add AUTH_ENABLED to AppConfig)
- **Wave**: 1
- **Owns**: `frontend/src/types/config.d.ts` (modify)
- **Reads**: [current `frontend/src/types/config.d.ts`]
- **Depends on**: none
- **Spec excerpt**:
  > `frontend/src/types/config.d.ts` — añadir `AUTH_ENABLED: string` a `interface AppConfig` (queda como string; la coerción a boolean vive en `config.ts`).
  > ```ts
  > declare global {
  >   interface AppConfig {
  >     API_URL: string;
  >     AUTH_ENABLED: string;
  >   }
  >   interface Window {
  >     __APP_CONFIG__: AppConfig;
  >   }
  > }
  > export {};
  > ```
- **Acceptance criteria**:
  1. `AppConfig` has `AUTH_ENABLED: string` next to `API_URL: string`.
  2. The rest of the file (Window interface, `export {};`) is unchanged.
- **Subagent prompt**:
  ```
  Eres el subagente U3 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (modifies):
  - frontend/src/types/config.d.ts

  NOT_TOUCH:
  - any other file

  READS:
  - frontend/src/types/config.d.ts (current state — read first, it currently only has `API_URL: string`)
  - AGENTS.md

  Spec excerpt (verbatim):
  > `frontend/src/types/config.d.ts` — añadir `AUTH_ENABLED: string` a `interface AppConfig` (queda como string; la coerción a boolean vive en `config.ts`).
  > ```ts
  > declare global {
  >   interface AppConfig {
  >     API_URL: string;
  >     AUTH_ENABLED: string;
  >   }
  >   interface Window {
  >     __APP_CONFIG__: AppConfig;
  >   }
  > }
  > export {};
  > ```

  Acceptance criteria:
  1. `AppConfig` interface has BOTH `API_URL: string` and `AUTH_ENABLED: string`.
  2. `Window.__APP_CONFIG__` and `export {};` are preserved verbatim.

  Report back:
  - Files modified
  - Any deviation
  - Any blocker
  ```

### U4: public/config.template.js (envsubst template)
- **Wave**: 1
- **Owns**: `frontend/public/config.template.js` (modify)
- **Reads**: [current `frontend/public/config.template.js`, `frontend/public/config.js`]
- **Depends on**: none
- **Spec excerpt**:
  > `frontend/public/config.template.js` — añadir `AUTH_ENABLED: "${AUTH_ENABLED}"` al objeto `window.__APP_CONFIG__`.
- **Acceptance criteria**:
  1. Template contains `AUTH_ENABLED: "${AUTH_ENABLED}"` next to `API_URL: "${API_URL}"`.
  2. Do NOT touch `frontend/public/config.js` (the runtime non-template file; it stays without AUTH_ENABLED for dev fallback).
- **Subagent prompt**:
  ```
  Eres el subagente U4 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (modifies):
  - frontend/public/config.template.js

  NOT_TOUCH:
  - frontend/public/config.js (runtime fallback, do NOT add AUTH_ENABLED here)
  - any other file

  READS:
  - frontend/public/config.template.js (current: only API_URL)
  - frontend/public/config.js (reference — do NOT modify)
  - AGENTS.md

  Spec excerpt (verbatim):
  > `frontend/public/config.template.js` — añadir `AUTH_ENABLED: "${AUTH_ENABLED}"` al objeto `window.__APP_CONFIG__`.

  Current template content:
  ```js
  window.__APP_CONFIG__ = {
    API_URL: "${API_URL}"
  };
  ```

  Desired final template:
  ```js
  window.__APP_CONFIG__ = {
    API_URL: "${API_URL}",
    AUTH_ENABLED: "${AUTH_ENABLED}"
  };
  ```

  Acceptance criteria:
  1. Template has both `API_URL` and `AUTH_ENABLED` placeholders.
  2. Valid JavaScript (no trailing comma issues).

  Report back:
  - Files modified
  - Any deviation
  - Any blocker
  ```

### U5: features/auth/api.ts (loginRequest)
- **Wave**: 2
- **Owns**: `frontend/src/features/auth/api.ts` (create)
- **Reads**: [`frontend/src/features/calendar/api.ts` (reference pattern), `frontend/src/api.ts`]
- **Depends on**: U1 (uses `LoginPayload`, `LoginResponse` from `./types`)
- **Spec excerpt**:
  > `features/auth/api.ts` — `loginRequest(payload)` que llama `api.post<LoginResponse>("/auth/login", payload)` y devuelve la respuesta.
  > ```ts
  > import { api } from "@/api";
  > import type { LoginPayload, LoginResponse } from "./types";
  > export async function loginRequest(payload: LoginPayload): Promise<LoginResponse> {
  >   const { data } = await api.post<LoginResponse>("/auth/login", payload);
  >   return data;
  > }
  > ```
- **Acceptance criteria**:
  1. Exports `loginRequest(payload: LoginPayload): Promise<LoginResponse>` exactly as in the spec.
- **Subagent prompt**:
  ```
  Eres el subagente U5 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (creates):
  - frontend/src/features/auth/api.ts

  NOT_TOUCH:
  - any other file

  READS:
  - frontend/src/features/calendar/api.ts (api pattern reference)
  - frontend/src/api.ts (axios instance)
  - frontend/src/features/auth/types.ts (produced by U1 — `LoginPayload`, `LoginResponse` interfaces)
  - AGENTS.md

  Spec excerpt (verbatim):
  > `features/auth/api.ts` — `loginRequest(payload)` que llama `api.post<LoginResponse>("/auth/login", payload)` y devuelve la respuesta.
  > ```ts
  > import { api } from "@/api";
  > import type { LoginPayload, LoginResponse } from "./types";
  >
  > export async function loginRequest(payload: LoginPayload): Promise<LoginResponse> {
  >   const { data } = await api.post<LoginResponse>("/auth/login", payload);
  >   return data;
  > }
  > ```

  Conventions:
  - Imports order: stdlib → third-party (`@/...`) → local (`./...`), alphabetical.
  - Biome formatting (tabs, double quotes).

  Acceptance criteria:
  1. Single named export `loginRequest` with the exact implementation.
  2. Imports `api` from `@/api` and the types from `./types`.

  Report back:
  - Files created
  - Any deviation
  - Any blocker
  ```

### U6: features/auth/hooks/use-login.ts (mutation hook)
- **Wave**: 2
- **Owns**: `frontend/src/features/auth/hooks/use-login.ts` (create)
- **Reads**: [`frontend/src/auth.tsx` (useAuth), `frontend/src/features/downloads/hooks/use-download-progress.ts` (hook pattern), `frontend/src/main.tsx` (RouterProvider context)]
- **Depends on**: U1 (types), U2 (parseLoginError), U5 (loginRequest)
- **Spec excerpt**:
  > `features/auth/hooks/use-login.ts` — hook con state de form (`username`, `password`, `showPassword`), `useMutation`, `handleSubmit`, navegación a `?redirect=` o `/home` en éxito, toast en error.
  > [verbatim code block in spec, lines 174-221]
- **Acceptance criteria**:
  1. Exports `useLogin()` with the exact implementation from the spec.
  2. Uses `useAuth().login` to store the token, and `toast.error` for failures.
  3. Navigation uses `?redirect=` if present, else `/home`, with `replace: true`.
- **Subagent prompt**:
  ```
  Eres el subagente U6 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (creates):
  - frontend/src/features/auth/hooks/use-login.ts

  NOT_TOUCH:
  - any other file

  READS:
  - frontend/src/auth.tsx (useAuth contract: `login(token: string)` decodes JWT and stores it)
  - frontend/src/features/auth/api.ts (U5 produced — `loginRequest`)
  - frontend/src/features/auth/lib/parse-login-error.ts (U2 produced — `parseLoginError`)
  - frontend/src/features/auth/types.ts (U1 produced — `LoginPayload`)
  - frontend/src/features/downloads/hooks/use-download-progress.ts (hook pattern)
  - AGENTS.md

  Spec excerpt (verbatim from `tasks/14-login-page.md` lines 174-221):
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

  Conventions:
  - Imports order: stdlib → third-party (`@/...`) → local (`../...`), alphabetical.
  - Biome formatting (tabs, double quotes).
  - No `any`; explicit types.

  Acceptance criteria:
  1. Exports `useLogin` with the exact code above.
  2. `useSearch({ from: "/login" })` reads the `redirect` search param (typed implicitly by TanStack Router when login route declares `validateSearch`).
  3. On success: `login(data.payload.access)` then `router.navigate({ to: search.redirect ?? "/home", replace: true })`.
  4. On error: `toast.error(parseLoginError(error))`.

  Report back:
  - Files created
  - Any deviation
  - Any blocker
  ```

### U7: config.ts (isAuthEnabled boolean)
- **Wave**: 2
- **Owns**: `frontend/src/config.ts` (modify)
- **Reads**: [current `frontend/src/config.ts`, `frontend/src/types/config.d.ts` after U3]
- **Depends on**: U3 (`AppConfig.AUTH_ENABLED` exists)
- **Spec excerpt**:
  > `frontend/src/config.ts` — añadir `export const isAuthEnabled: boolean = config.AUTH_ENABLED === "true"`.
- **Acceptance criteria**:
  1. Exports `isAuthEnabled: boolean` derived from `config.AUTH_ENABLED === "true"`.
  2. The existing `export const config: AppConfig = window.__APP_CONFIG__;` line is preserved.
- **Subagent prompt**:
  ```
  Eres el subagente U7 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (modifies):
  - frontend/src/config.ts

  NOT_TOUCH:
  - any other file

  READS:
  - frontend/src/config.ts (current: single line `export const config: AppConfig = window.__APP_CONFIG__;`)
  - frontend/src/types/config.d.ts (U3 produced — now declares `AUTH_ENABLED: string` on `AppConfig`)
  - AGENTS.md

  Spec excerpt (verbatim):
  > `frontend/src/config.ts` — añadir `export const isAuthEnabled: boolean = config.AUTH_ENABLED === "true"`.

  Current file:
  ```ts
  export const config: AppConfig = window.__APP_CONFIG__;
  ```

  Desired final file (preserve the existing line, add the new one after):
  ```ts
  export const config: AppConfig = window.__APP_CONFIG__;

  export const isAuthEnabled: boolean = config.AUTH_ENABLED === "true";
  ```

  Conventions:
  - Biome formatting (tabs, double quotes).
  - No `any`; explicit type annotation on the export.

  Acceptance criteria:
  1. Both `config` and `isAuthEnabled` are exported.
  2. `isAuthEnabled` is typed as `boolean`.

  Report back:
  - Files modified
  - Any deviation
  - Any blocker
  ```

### U8: features/auth/components/login-header.tsx
- **Wave**: 3
- **Owns**: `frontend/src/features/auth/components/login-header.tsx` (create)
- **Reads**: [`frontend/src/features/calendar/components/calendar-header.tsx` (header pattern), `frontend/src/features/home/components/home-welcome.tsx` (Card usage), `frontend/src/components/ui/card.tsx`]
- **Depends on**: none (no app code deps; uses lucide-react)
- **Spec excerpt**:
  > ### A · Header
  > Icono decorativo + título + subtítulo + link "Sign up".
  > - Icono `Clapperboard` (lucide) `size-10 text-muted-foreground`.
  > - `h1` "Welcome to Ani Seek" con `text-2xl font-bold tracking-tight`.
  > - `p` "A simple way to scrap anime" con `text-sm text-muted-foreground`.
  > - Línea de CTA: texto `Don't have an account?` + `<Link to="/register" className="text-primary underline-offset-4 hover:underline">Sign up</Link>`.
  > - Layout: `flex flex-col items-center gap-2 text-center`.
- **Acceptance criteria**:
  1. Exports `LoginHeader()` (no props).
  2. Renders `Clapperboard` icon (size-10, text-muted-foreground), `h1` "Welcome to Ani Seek", `p` "A simple way to scrap anime", and a `Link to="/register"` styled as primary underline-on-hover.
  3. Outer container: `flex flex-col items-center gap-2 text-center`.
- **Subagent prompt**:
  ```
  Eres el subagente U8 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (creates):
  - frontend/src/features/auth/components/login-header.tsx

  NOT_TOUCH:
  - any other file

  READS:
  - frontend/src/features/calendar/components/calendar-header.tsx (header pattern)
  - frontend/src/features/home/components/home-welcome.tsx (Card usage and class patterns)
  - frontend/src/components/ui/card.tsx (Card primitives available)
  - AGENTS.md

  Spec excerpt (verbatim from `tasks/14-login-page.md` "### A · Header"):
  > Icono decorativo + título + subtítulo + link "Sign up".
  > - Icono `Clapperboard` (lucide) `size-10 text-muted-foreground`.
  > - `h1` "Welcome to Ani Seek" con `text-2xl font-bold tracking-tight`.
  > - `p` "A simple way to scrap anime" con `text-sm text-muted-foreground`.
  > - Línea de CTA: texto `Don't have an account?` + `<Link to="/register" className="text-primary underline-offset-4 hover:underline">Sign up</Link>`.
  > - Layout: `flex flex-col items-center gap-2 text-center`.

  Conventions:
  - Import `Link` from `@tanstack/react-router`.
  - Import `Clapperboard` from `lucide-react`.
  - No `any`; explicit types.
  - Imports order: stdlib → third-party → local, alphabetical.
  - Biome formatting (tabs, double quotes).

  Acceptance criteria:
  1. Exports `LoginHeader()` (no props).
  2. Renders all 4 elements (icon, h1, p, CTA with Link).
  3. Outer wrapper: `flex flex-col items-center gap-2 text-center`.

  Report back:
  - Files created
  - Any deviation
  - Any blocker
  ```

### U9: features/auth/components/login-footer.tsx
- **Wave**: 3
- **Owns**: `frontend/src/features/auth/components/login-footer.tsx` (create)
- **Reads**: [`frontend/src/components/ui/separator.tsx` (Separator usage)]
- **Depends on**: none
- **Spec excerpt**:
  > ### C · Footer
  > Dos enlaces externos separados por `Separator orientation="vertical"`.
  > - `<a href="https://github.com/ElPitagoras14/aniseek" target="_blank" rel="noreferrer">` con `Github` icon + texto "Github".
  > - `Separator orientation="vertical" className="h-4"`.
  > - `<a href="https://buymeacoffee.com/jhonyg" target="_blank" rel="noreferrer">` con `Coffee` icon + texto "Support it".
  > - Layout: `flex items-center justify-center gap-3 text-sm text-muted-foreground`.
- **Acceptance criteria**:
  1. Exports `LoginFooter()` (no props).
  2. Two `<a>` with `target="_blank" rel="noreferrer"`, separated by a vertical `Separator`.
  3. Outer wrapper: `flex items-center justify-center gap-3 text-sm text-muted-foreground`.
- **Subagent prompt**:
  ```
  Eres el subagente U9 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (creates):
  - frontend/src/features/auth/components/login-footer.tsx

  NOT_TOUCH:
  - any other file

  READS:
  - frontend/src/components/ui/separator.tsx (Separator props: `orientation`, `decorative`)
  - AGENTS.md

  Spec excerpt (verbatim from `tasks/14-login-page.md` "### C · Footer"):
  > Dos enlaces externos separados por `Separator orientation="vertical"`.
  > - `<a href="https://github.com/ElPitagoras14/aniseek" target="_blank" rel="noreferrer">` con `Github` icon + texto "Github".
  > - `Separator orientation="vertical" className="h-4"`.
  > - `<a href="https://buymeacoffee.com/jhonyg" target="_blank" rel="noreferrer">` con `Coffee` icon + texto "Support it".
  > - Layout: `flex items-center justify-center gap-3 text-sm text-muted-foreground`.

  Conventions:
  - Import `Coffee` and `Github` from `lucide-react`.
  - Import `Separator` from `@/components/ui/separator`.
  - Icons: `<Github className="size-4" />` next to the link text.
  - No `any`.
  - Biome formatting (tabs, double quotes).

  Acceptance criteria:
  1. Exports `LoginFooter()` (no props).
  2. Two `<a>` with `target="_blank" rel="noreferrer"`.
  3. A vertical `Separator` between them.
  4. Outer wrapper: `flex items-center justify-center gap-3 text-sm text-muted-foreground`.

  Report back:
  - Files created
  - Any deviation
  - Any blocker
  ```

### U10: features/auth/components/login-form.tsx + components/ui/label.tsx
- **Wave**: 3
- **Owns**: `frontend/src/features/auth/components/login-form.tsx` (create), `frontend/src/components/ui/label.tsx` (create — shadcn primitive required by the form, missing from the project)
- **Reads**: [`frontend/src/features/auth/hooks/use-login.ts` (U6), `frontend/src/components/ui/input.tsx`, `frontend/src/components/ui/button.tsx`, `frontend/src/components/not-found.tsx` for Card usage if any]
- **Depends on**: U6 (useLogin hook)
- **Spec excerpt**:
  > ### B · Form
  > Form controlado por el hook `useLogin()` con dos inputs y un botón.
  > - `Label` + `Input` para `username` con `autoComplete="username"`, `name="username"`, `required`, `placeholder="Username"`.
  > - `Label` + `Input` para `password` con `type={showPassword ? "text" : "password"}`, `autoComplete="current-password"`, `name="password"`, `required`. Wrapper relativo con botón absoluto a la derecha que alterna `Eye` / `EyeOff` (lucide).
  > - `Button type="submit"` full width, texto "Login", `disabled={isPending}`. Cuando `isPending` muestra `Loader2Icon animate-spin` a la izquierda del texto.
  > - Layout: `flex flex-col gap-4` dentro de un `<form onSubmit={handleSubmit}>`.
- **Acceptance criteria**:
  1. `Label` shadcn primitive exists at `frontend/src/components/ui/label.tsx` and exports `Label` (standard shadcn file using `@radix-ui/react-label`).
  2. `LoginForm()` uses `useLogin()` and renders username + password inputs with the show/hide toggle.
  3. Submit button is full width, shows `Loader2 animate-spin` + "Login" text when `isPending`.
  4. Each `Input` has an associated `Label htmlFor` matching its `id`.
  5. Outer wrapper: `flex flex-col gap-4` inside `<form onSubmit={handleSubmit}>`.
- **Subagent prompt**:
  ```
  Eres el subagente U10 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (creates):
  - frontend/src/features/auth/components/login-form.tsx
  - frontend/src/components/ui/label.tsx

  NOT_TOUCH:
  - any other file (in particular: do NOT modify login-card, login-header, login-footer, login route, etc.)

  READS:
  - frontend/src/features/auth/hooks/use-login.ts (U6 produced — `useLogin` returns `{ username, setUsername, password, setPassword, showPassword, setShowPassword, isPending, handleSubmit }`)
  - frontend/src/components/ui/input.tsx (Input component)
  - frontend/src/components/ui/button.tsx (Button component)
  - AGENTS.md

  Spec excerpt (verbatim from `tasks/14-login-page.md` "### B · Form"):
  > Form controlado por el hook `useLogin()` con dos inputs y un botón.
  > - `Label` + `Input` para `username` con `autoComplete="username"`, `name="username"`, `required`, `placeholder="Username"`.
  > - `Label` + `Input` para `password` con `type={showPassword ? "text" : "password"}`, `autoComplete="current-password"`, `name="password"`, `required`. Wrapper relativo con botón absoluto a la derecha que alterna `Eye` / `EyeOff` (lucide).
  > - `Button type="submit"` full width, texto "Login", `disabled={isPending}`. Cuando `isPending` muestra `Loader2Icon animate-spin` a la izquierda del texto.
  > - Layout: `flex flex-col gap-4` dentro de un `<form onSubmit={handleSubmit}>`.

  Implementation guidance for the two files:

  1. `frontend/src/components/ui/label.tsx` — standard shadcn `Label` primitive wrapping `@radix-ui/react-label` (or the `radix-ui` package — check which one the project uses; from `frontend/src/components/ui/separator.tsx` it uses `import { Separator as SeparatorPrimitive } from "radix-ui"`, so use `import { Label as LabelPrimitive } from "radix-ui"`). Use the same file style as `frontend/src/components/ui/separator.tsx`. Add `data-slot="label"` and `cn()` for class merging. Export the named `Label` component.

  2. `frontend/src/features/auth/components/login-form.tsx`:
     - Call `const { username, setUsername, password, setPassword, showPassword, setShowPassword, isPending, handleSubmit } = useLogin();`
     - Import: `Label` from `@/components/ui/label`, `Input` from `@/components/ui/input`, `Button` from `@/components/ui/button`, icons `Eye`, `EyeOff`, `Loader2` from `lucide-react`, and the `useLogin` hook from `@/features/auth/hooks/use-login`.
     - Render:
       ```tsx
       <form onSubmit={handleSubmit} className="flex flex-col gap-4">
         <div className="flex flex-col gap-2">
           <Label htmlFor="username">Username</Label>
           <Input id="username" name="username" type="text" autoComplete="username" required placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} disabled={isPending} />
         </div>
         <div className="flex flex-col gap-2">
           <Label htmlFor="password">Password</Label>
           <div className="relative">
             <Input id="password" name="password" type={showPassword ? "text" : "password"} autoComplete="current-password" required placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} disabled={isPending} className="pr-10" />
             <Button type="button" variant="ghost" size="icon" onClick={() => setShowPassword((s) => !s)} className="absolute right-0 top-0 h-full px-3" aria-label={showPassword ? "Hide password" : "Show password"}>
               {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
             </Button>
           </div>
         </div>
         <Button type="submit" disabled={isPending} className="w-full">
           {isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
           Login
         </Button>
       </form>
       ```

  Conventions:
  - No `any`; explicit types.
  - Imports order: stdlib → third-party → local, alphabetical.
  - Biome formatting (tabs, double quotes).

  Acceptance criteria:
  1. `frontend/src/components/ui/label.tsx` exists and exports `Label`.
  2. `frontend/src/features/auth/components/login-form.tsx` exports `LoginForm()` (no props) and matches the spec markup.
  3. Username input has `id="username"`, `name="username"`, `autoComplete="username"`, `required`.
  4. Password input has `id="password"`, `name="password"`, `autoComplete="current-password"`, `required`, type toggled by `showPassword`.
  5. Submit button is full width, shows `Loader2 animate-spin` next to "Login" when `isPending`.

  Report back:
  - Files created
  - Any deviation
  - Any blocker
  ```

### U11: features/auth/components/login-card.tsx (card orchestrator)
- **Wave**: 4
- **Owns**: `frontend/src/features/auth/components/login-card.tsx` (create)
- **Reads**: [`frontend/src/components/ui/card.tsx`, `frontend/src/components/ui/separator.tsx`, U8/U9/U10 outputs]
- **Depends on**: U8 (header), U9 (footer), U10 (form)
- **Spec excerpt**:
  > Pantalla `/login` con fondo `bg-background`, contenido centrado vertical y horizontalmente. Un único `Card` con tres secciones separadas por `Separator`: header, form y footer.
- **Acceptance criteria**:
  1. Exports `LoginCard()` (no props).
  2. Renders a single `Card` containing `<LoginHeader />`, `<Separator />`, `<LoginForm />`, `<Separator />`, `<LoginFooter />`.
  3. Card has responsive width: `w-full max-w-sm sm:max-w-md mx-auto` and the page wrapper is `min-h-svh flex items-center justify-center p-4 bg-background` (the route will wrap the card; the card itself should be centered on the page).
- **Subagent prompt**:
  ```
  Eres el subagente U11 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (creates):
  - frontend/src/features/auth/components/login-card.tsx

  NOT_TOUCH:
  - any other file

  READS:
  - frontend/src/components/ui/card.tsx (Card primitives)
  - frontend/src/components/ui/separator.tsx (Separator)
  - frontend/src/features/auth/components/login-header.tsx (U8 produced — `LoginHeader`)
  - frontend/src/features/auth/components/login-form.tsx (U10 produced — `LoginForm`)
  - frontend/src/features/auth/components/login-footer.tsx (U9 produced — `LoginFooter`)
  - AGENTS.md

  Spec excerpt (verbatim from "## Vista"):
  > Pantalla `/login` con fondo `bg-background`, contenido centrado vertical y horizontalmente. Un único `Card` con tres secciones separadas por `Separator`: header, form y footer.
  >
  > ## Layout responsive
  > | Breakpoint | Comportamiento |
  > |---|---|
  > | `< sm` (< 640px) | Card `w-full`, padding `p-4`, footer horizontal (sin wrap) |
  > | `sm` (≥ 640px) | Card `max-w-sm`, `mx-auto` |
  > | `md+` (≥ 768px) | Card `max-w-md`, `mx-auto` |
  >
  > Wrapper de la página: `min-h-svh flex items-center justify-center p-4`.

  Implementation:
  ```tsx
  import { Card, CardContent } from "@/components/ui/card";
  import { Separator } from "@/components/ui/separator";
  import { LoginFooter } from "./login-footer";
  import { LoginForm } from "./login-form";
  import { LoginHeader } from "./login-header";

  export function LoginCard() {
    return (
      <div className="min-h-svh flex items-center justify-center p-4 bg-background">
        <Card className="w-full max-w-sm sm:max-w-md mx-auto">
          <CardContent className="p-4 sm:p-6 flex flex-col gap-4">
            <LoginHeader />
            <Separator />
            <LoginForm />
            <Separator />
            <LoginFooter />
          </CardContent>
        </Card>
      </div>
    );
  }
  ```

  Conventions:
  - Imports order: stdlib → third-party (`@/...`) → local (`./...`), alphabetical.
  - Biome formatting (tabs, double quotes).

  Acceptance criteria:
  1. Exports `LoginCard()` (no props).
  2. Single `Card` containing `LoginHeader` + `Separator` + `LoginForm` + `Separator` + `LoginFooter` in that order.
  3. Responsive width `w-full max-w-sm sm:max-w-md mx-auto` on the Card.
  4. Page wrapper `min-h-svh flex items-center justify-center p-4 bg-background`.

  Report back:
  - Files created
  - Any deviation
  - Any blocker
  ```

### U12: routes/register.tsx (stub)
- **Wave**: 4
- **Owns**: `frontend/src/routes/register.tsx` (create)
- **Reads**: [`frontend/src/routes/_app/profile.tsx` (stub pattern)]
- **Depends on**: none
- **Spec excerpt**:
  > `frontend/src/routes/register.tsx` — stub (`<div>Hello "/register"!</div>`) listo para el spec de registro.
- **Acceptance criteria**:
  1. File exists with `createFileRoute("/register")` and a component returning `<div>Hello "/register"!</div>`.
- **Subagent prompt**:
  ```
  Eres el subagente U12 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (creates):
  - frontend/src/routes/register.tsx

  NOT_TOUCH:
  - any other file

  READS:
  - frontend/src/routes/_app/profile.tsx (stub route pattern)
  - AGENTS.md

  Spec excerpt (verbatim):
  > `frontend/src/routes/register.tsx` — stub (`<div>Hello "/register"!</div>`) listo para el spec de registro.

  Implementation (mirror `frontend/src/routes/_app/profile.tsx`):
  ```tsx
  import { createFileRoute } from "@tanstack/react-router";

  export const Route = createFileRoute("/register")({
    component: RouteComponent,
  });

  function RouteComponent() {
    return <div>Hello "/register"!</div>;
  }
  ```

  Conventions:
  - Biome formatting (tabs, double quotes).

  Acceptance criteria:
  1. File exists with the exact content above.
  2. Route id is `/register`.

  Report back:
  - Files created
  - Any deviation
  - Any blocker
  ```

### U13: routes/_app/route.tsx (auth-gated guard)
- **Wave**: 5
- **Owns**: `frontend/src/routes/_app/route.tsx` (modify)
- **Reads**: [current `frontend/src/routes/_app/route.tsx`, `frontend/src/config.ts` (U7), `frontend/src/auth.tsx` (useAuth)]
- **Depends on**: U7 (isAuthEnabled)
- **Spec excerpt**:
  > `frontend/src/routes/_app/route.tsx` — el guard actual hace auto-login hardcodeado siempre. Cambiar para que:
  >   - Si `!isAuthEnabled`: comportamiento actual (auto-login con `admin`/`admin123`).
  >   - Si `isAuthEnabled && !context.auth.isAuthenticated`: `throw redirect({ to: "/login", search: { redirect: location.href } })`.
- **Acceptance criteria**:
  1. When `!isAuthEnabled`, the existing auto-login with `admin`/`admin123` still runs.
  2. When `isAuthEnabled && !context.auth.isAuthenticated`, throw a `redirect` to `/login` with `search: { redirect: location.href }`.
  3. The local `interface LoginResponse` is replaced by the import from `@/features/auth/types` (or kept if simpler — but ideally import).
  4. The rest of the component (`<SidebarProvider>...`) is preserved.
- **Subagent prompt**:
  ```
  Eres el subagente U13 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está estrictamente delimitado a los archivos en OWNS.

  OWNS (modifies):
  - frontend/src/routes/_app/route.tsx

  NOT_TOUCH:
  - any other file

  READS:
  - frontend/src/routes/_app/route.tsx (current: hardcoded auto-login)
  - frontend/src/config.ts (U7 produced — `isAuthEnabled` boolean)
  - frontend/src/features/auth/api.ts (U5 — `loginRequest`) OR keep using `api.post` directly as the original did
  - frontend/src/auth.tsx (useAuth contract)
  - AGENTS.md

  Spec excerpt (verbatim from `tasks/14-login-page.md` "### Modificar"):
  > `frontend/src/routes/_app/route.tsx` — el guard actual hace auto-login hardcodeado siempre. Cambiar para que:
  >   - Si `!isAuthEnabled`: comportamiento actual (auto-login con `admin`/`admin123`).
  >   - Si `isAuthEnabled && !context.auth.isAuthenticated`: `throw redirect({ to: "/login", search: { redirect: location.href } })`.

  Current file content (verbatim):
  ```tsx
  import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
  import { api } from "@/api";
  import { NotFoundContent } from "@/components/not-found";
  import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
  import { TooltipProvider } from "@/components/ui/tooltip";
  import { AppSidebar } from "@/features/root/components/app-sidebar";
  import { MobileHeader } from "@/features/root/components/mobile-header";

  interface LoginResponse {
    payload: { access: string; refresh: string };
  }

  export const Route = createFileRoute("/_app")({
    beforeLoad: async ({ context, location }) => {
      if (!context.auth.isAuthenticated) {
        try {
          const { data } = await api.post<LoginResponse>("/auth/login", {
            username: "admin",
            password: "admin123",
          });
          context.auth.login(data.payload.access);
        } catch {
          throw redirect({
            to: "/login",
            search: { redirect: location.href },
          });
        }
      }
    },
    component: RouteComponent,
    notFoundComponent: NotFoundContent,
  });

  function RouteComponent() {
    return (
      <div>
        <SidebarProvider>
          <TooltipProvider>
            <AppSidebar variant="sidebar" />
            <SidebarInset>
              <MobileHeader />
              <Outlet />
            </SidebarInset>
          </TooltipProvider>
        </SidebarProvider>
      </div>
    );
  }
  ```

  Desired `beforeLoad` (replace the existing one only — keep everything else):
  ```ts
  beforeLoad: async ({ context, location }) => {
    if (!isAuthEnabled) {
      if (!context.auth.isAuthenticated) {
        try {
          const { data } = await api.post<LoginResponse>("/auth/login", {
            username: "admin",
            password: "admin123",
          });
          context.auth.login(data.payload.access);
        } catch {
          throw redirect({
            to: "/login",
            search: { redirect: location.href },
          });
        }
      }
      return;
    }
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: "/login",
        search: { redirect: location.href },
      });
    }
  },
  ```

  Add at top (alphabetical, third-party after stdlib, before local):
  ```ts
  import { isAuthEnabled } from "@/config";
  ```

  Conventions:
  - Imports order: stdlib → third-party (`@/...`) → local, alphabetical.
  - Biome formatting (tabs, double quotes).
  - Keep the local `interface LoginResponse` as-is (it has the minimal shape `{ payload: { access, refresh } }` and matches what `api.post<LoginResponse>` expects — do not refactor to import from `@/features/auth/types` unless trivial).

  Acceptance criteria:
  1. When `!isAuthEnabled` and unauthenticated: auto-login with `admin`/`admin123` is attempted; on failure, redirect to `/login?redirect=...`.
  2. When `isAuthEnabled` and unauthenticated: redirect to `/login?redirect=...` without calling the API.
  3. When authenticated: pass through.
  4. `isAuthEnabled` is imported from `@/config`.
  5. The `RouteComponent` and `notFoundComponent` are unchanged.

  Report back:
  - Files modified
  - Any deviation
  - Any blocker
  ```

### U14: routes/login.tsx (route orchestrator — FINAL)
- **Wave**: 5
- **Owns**: `frontend/src/routes/login.tsx` (modify)
- **Reads**: [current `frontend/src/routes/login.tsx`, `frontend/src/routes/_app/route.tsx` (U13) for reference on the redirect pattern, `frontend/src/config.ts` (U7), `frontend/src/auth.tsx` (useAuth), `frontend/src/api.ts`, `frontend/src/features/auth/api.ts` (U5), `frontend/src/features/auth/types.ts` (U1), `frontend/src/features/auth/components/login-card.tsx` (U11)]
- **Depends on**: U1, U5, U7, U11 (and uses U12 register stub via Link)
- **Spec excerpt**:
  > `frontend/src/routes/login.tsx` — reemplazar stub por `RouteComponent` que renderiza `<LoginCard />`. Añadir `validateSearch` con `redirect?: string`. `beforeLoad`: si `!isAuthEnabled`, ejecutar auto-login con `admin`/`admin123` y `throw redirect({ to: "/home" })`; si `isAuthEnabled && context.auth.isAuthenticated`, `throw redirect({ to: search.redirect ?? "/home" })`.
- **Acceptance criteria**:
  1. File replaces the stub with a `RouteComponent` that renders `<LoginCard />`.
  2. `validateSearch` accepts an optional `redirect: string` query param.
  3. `beforeLoad`:
     - `if (!isAuthEnabled)`: try auto-login with `admin`/`admin123`; on success, call `context.auth.login(access)` and `throw redirect({ to: "/home" })`. (If auto-login throws, fall through to show the form — but in practice this won't fail.)
     - `else if (context.auth.isAuthenticated)`: `throw redirect({ to: search.redirect ?? "/home" })`.
  4. The TanStack `register` declaration for the route's search type is added (using `declare module "@tanstack/react-router"` if needed for typed search).
- **Subagent prompt**:
  ```
  Eres el subagente U14 del plan `tasks/15-login-page-parallel.md`. Tu trabajo está delimitado a los archivos en OWNS. Eres el ÚLTIMO subagente: integras todo.

  OWNS (modifies):
  - frontend/src/routes/login.tsx

  NOT_TOUCH:
  - any other file (in particular: do NOT modify `_app/route.tsx` — that's U13's job)

  READS:
  - frontend/src/routes/login.tsx (current: stub)
  - frontend/src/routes/_app/route.tsx (U13 produced — same auto-login pattern reference)
  - frontend/src/config.ts (U7 — `isAuthEnabled`)
  - frontend/src/auth.tsx (useAuth: `login(token)` stores token and decodes user)
  - frontend/src/api.ts (axios instance with `/api` base)
  - frontend/src/features/auth/api.ts (U5 — `loginRequest(payload)`)
  - frontend/src/features/auth/types.ts (U1 — `LoginPayload`, `LoginResponse`)
  - frontend/src/features/auth/components/login-card.tsx (U11 — `LoginCard`)
  - AGENTS.md

  Spec excerpt (verbatim from `tasks/14-login-page.md` "### Modificar"):
  > `frontend/src/routes/login.tsx` — reemplazar stub por `RouteComponent` que renderiza `<LoginCard />`. Añadir `validateSearch` con `redirect?: string`. `beforeLoad`: si `!isAuthEnabled`, ejecutar auto-login con `admin`/`admin123` y `throw redirect({ to: "/home" })`; si `isAuthEnabled && context.auth.isAuthenticated`, `throw redirect({ to: search.redirect ?? "/home" })`.

  Current file content (verbatim):
  ```tsx
  import { createFileRoute } from "@tanstack/react-router";

  export const Route = createFileRoute("/login")({
    component: RouteComponent,
  });

  function RouteComponent() {
    return <div>Hello "/login"!</div>;
  }
  ```

  Desired final file:
  ```tsx
  import { createFileRoute, redirect } from "@tanstack/react-router";
  import { z } from "zod";
  import { api } from "@/api";
  import { useAuth } from "@/auth";
  import { isAuthEnabled } from "@/config";
  import { LoginCard } from "@/features/auth/components/login-card";

  const loginSearchSchema = z.object({
    redirect: z.string().optional(),
  });

  export const Route = createFileRoute("/login")({
    validateSearch: loginSearchSchema,
    beforeLoad: async ({ context, search }) => {
      if (!isAuthEnabled) {
        try {
          const { data } = await api.post<{ payload: { access: string } }>(
            "/auth/login",
            { username: "admin", password: "admin123" },
          );
          context.auth.login(data.payload.access);
        } catch {
          // fall through and show the form
        }
        throw redirect({ to: "/home" });
      }
      if (context.auth.isAuthenticated) {
        throw redirect({ to: search.redirect ?? "/home" });
      }
    },
    component: RouteComponent,
  });

  function RouteComponent() {
    useAuth();
    return <LoginCard />;
  }
  ```

  Notes:
  - `zod` is already a transitive dep (TanStack Router uses it for `validateSearch`); if you find it's not directly listed, check `package.json`. The codebase pattern uses `z.object` (zod v3) — confirm by searching the project. If zod is not available, fall back to declaring a TS interface and using `(search) => ({ redirect: typeof (search as Record<string, unknown>).redirect === "string" ? (search as Record<string, unknown>).redirect as string : undefined })` — but zod is the idiomatic approach for TanStack Router. Verify by reading how other routes use `validateSearch` (search the codebase: `grep -r "validateSearch" frontend/src/routes`).
  - `useAuth()` is called inside the component to make sure the context is available (matches the `auth: undefined!` initialization in `main.tsx` — the runtime context is injected via `<RouterProvider context={{ auth }}>` in `InnerApp`).
  - Imports order: stdlib → third-party (`@/...`) → local, alphabetical. (Note: `zod` is a third-party dep that resolves to a bare import — treat it like a stdlib import since it has no `@/` prefix; alphabetical order means `zod` comes AFTER `react` packages but BEFORE `@/api`. Check existing imports to confirm the project's Biome config does NOT enforce sort order strictly — but the spec says alphabetical stdlib→third-party→local.)

  Conventions:
  - No `any`.
  - No comments in the code.
  - Biome formatting (tabs, double quotes).

  Acceptance criteria:
  1. `validateSearch` accepts an optional `redirect: string`.
  2. `beforeLoad`:
     - If `!isAuthEnabled`: tries auto-login with `admin`/`admin123`, on success stores the token and `throw redirect({ to: "/home" })`.
     - Else if authenticated: `throw redirect({ to: search.redirect ?? "/home" })`.
  3. `RouteComponent` renders `<LoginCard />`.
  4. The `useAuth()` call is harmless (it returns the context) — it ensures the component participates in the auth tree; if you find it unnecessary, you may omit it.
  5. No `any` types.

  Report back:
  - Files modified
  - The exact import you used for `validateSearch` (zod vs raw) and why
  - Any deviation
  - Any blocker
  ```

## Execution waves

| Wave | UoWs | Parallelism | Notes |
|------|------|-------------|-------|
| 1 | U1, U2, U3, U4 | 4-way | types, lib, global config types, envsubst template — no app deps |
| 2 | U5, U6, U7 | 3-way | api (deps U1), hook (deps U1+U2+U5), config runtime (deps U3) |
| 3 | U8, U9, U10 | 3-way | header, footer, form+label (form depends on U6) |
| 4 | U11, U12 | 2-way | card orchestrator (deps U8+U9+U10), register stub (no deps) |
| 5 | U13, U14 | 2-way | _app guard (deps U7), login route orchestrator (deps U1+U5+U7+U11) |

## Integration step (parent agent)

After all waves complete, the parent agent:
1. Reads every file in every UoW's `Owns` list to confirm content.
2. Runs `pnpm exec biome check` in `frontend/` and `pnpm exec tsc --noEmit` in `frontend/`.
3. If both pass, updates the "Resultados" section of `tasks/14-login-page.md` with the table.
4. Reports back to the user: total files, lint/typecheck result, suggested commit message.
5. Does NOT commit, push, or open a PR without an explicit user request.

## Risk register

- U10 must create the `Label` shadcn primitive (the project has `Card`, `Input`, `Button`, `Separator` but no `Label`); the form depends on it. Acceptable — small isolated file.
- U14 depends on `zod` being available; if not directly listed in `package.json`, the subagent must check and use the fallback. zod is a TanStack Router peer dep, so it should be transitively available.
- U6 reads `useSearch({ from: "/login" })` — the typed `redirect` param only exists if U14 declares `validateSearch` with that schema. U6 will compile but `search.redirect` will be typed as `unknown` until U14 lands. Acceptable because U6 runs in wave 2, U14 in wave 5; the intermediate state is type-incomplete but functionally correct.
- U14 imports `LoginCard` from `@/features/auth/components/login-card`; this only resolves after U11 lands. Same wave ordering handles it.
- No UoW exceeds ~50 lines of new code — well under the 400-line cap.
- No wave has parallelism >4 — under the user's 5 cap.

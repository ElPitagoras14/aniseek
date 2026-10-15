## 1. Datos de navegación

- [x] 1.1 Agregar `mobile?: "bottom" | "account"` a `NavSection` en `features/root/sidebar-data.ts` y asignarlo (bottom: Home, Search, Saved, Calendar, Downloads; account: Storage, Profile; Franchises sin valor); verificar con `tsc --noEmit`
- [x] 1.2 Exponer helpers que devuelvan las secciones `bottom` y `account` en orden; verificar que `bottom` devuelve exactamente las 5 secciones en el orden de la spec

## 2. Componentes de navegación móvil

- [x] 2.1 Extraer el diálogo de confirmación de `NavUser` a `LogoutDialog` controlado y usarlo en `NavUser`; verificar que el logout desde el sidebar sigue pidiendo confirmación
- [x] 2.2 Crear `BottomNav` (fija abajo, `md:hidden`, ícono + etiqueta, `activeProps` para resaltar, padding de safe area, comentario apuntando a `MOBILE_BREAKPOINT`); verificar en 390px que un tap navega y resalta la sección con `aria-current="page"`
- [x] 2.3 Crear `AccountMenu` con `DropdownMenu` (usuario y rol, Profile, Storage, separador, Sign out que cierra el menú y abre `LogoutDialog`); verificar que Storage navega y cierra el menú, y que cancelar el logout mantiene la sesión
- [x] 2.4 Rehacer `MobileHeader`: marca a la izquierda, `AccountMenu` a la derecha, sin `SidebarTrigger`, `md:hidden`; verificar en 390px que no hay control para abrir el sidebar

## 3. Shell autenticado

- [x] 3.1 Crear `AppShell({ children })` con providers, `AppSidebar`, `SidebarInset` con `MobileHeader`, contenido con padding inferior (`calc(4rem + env(safe-area-inset-bottom))` bajo `md`, 0 desde `md`) y `BottomNav`
- [x] 3.2 Usar `AppShell` en `routes/_app/route.tsx` y en `NotFound` (`components/not-found.tsx`); verificar que una ruta inexistente autenticada en 390px muestra header y barra inferior
- [x] 3.3 Agregar `viewport-fit=cover` al meta viewport de `frontend/index.html`; verificar en emulación de iPhone (DevTools) que la barra queda sobre el área segura

## 4. Estado activo en el sidebar

- [x] 4.1 Marcar la sección activa en `NavMain` y `NavSecondary` (`isActive` de `SidebarMenuButton`); verificar en 1280px que Downloads aparece resaltado al estar en `/downloads` y solo ese ítem

## 5. Verificación y release

- [x] 5.1 Recorrer todas las páginas de `_app` (home, search, saved, calendar, downloads, storage, profile, detalle de anime) en 390px, 820px y 1280px: barra inferior solo en 390px, sidebar en 820px y 1280px, último contenido visible sobre la barra, overlays (dialogs, selects, toasts) por encima de la barra; verificar que al cruzar 768px el layout cambia sin recargar
- [x] 5.2 Ejecutar lint, typecheck y build del frontend sin errores
- [x] 5.3 Bumpear `VERSION` (minor) en el mismo PR

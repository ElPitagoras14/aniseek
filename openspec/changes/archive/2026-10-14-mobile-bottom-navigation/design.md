## Context

- El layout autenticado se arma en `routes/_app/route.tsx` (`SidebarProvider` → `AppSidebar` + `SidebarInset` con `MobileHeader` y `<Outlet/>`), y está duplicado en `NotFound` (`components/not-found.tsx`).
- `components/ui/sidebar.tsx` (shadcn) decide entre `Sheet` y sidebar fijo con `useIsMobile()` (768px) y usa clases `md:` para mostrar el sidebar de escritorio (`md:block`, `md:flex`) y estilos del inset.
- `useIsMobile` también lo usa `routes/_app/calendar.tsx` para forzar la vista por día.
- `features/root/sidebar-data.ts` define grupos y secciones (`NavGroup`, `NavSection`) que consumen `NavMain` y `NavSecondary`. `NavUser` contiene el diálogo de confirmación de logout.
- Los ítems del sidebar no marcan la ruta activa.
- `index.html` declara `width=device-width, initial-scale=1.0`, sin `viewport-fit`.

## Goals / Non-Goals

**Goals:**
- Mantener el concepto de "móvil" que ya existe (768px, default de shadcn), compartido por JS (`useIsMobile`) y CSS (Tailwind `md:`).
- Un shell autenticado único, reutilizado por la app y el 404.
- Una sola fuente de datos de navegación para sidebar, barra inferior y menú de cuenta.

**Non-Goals:**
- Cambiar el breakpoint móvil o editar `components/ui/sidebar.tsx` / `hooks/use-mobile.ts`.
- Rediseñar el sidebar de escritorio más allá del estado activo.
- Adaptar páginas, tablas o filtros (change posterior).
- Ocultar la barra con el scroll, gestos o animaciones de transición.

## Decisions

### D1 - Conservar el breakpoint por defecto de shadcn (768px)

shadcn define "móvil" en dos lugares independientes que coinciden en 768px: `MOBILE_BREAKPOINT` en `use-mobile.ts` (decide `Sheet` vs sidebar fijo) y las clases `md:` de `sidebar.tsx` (Tailwind v4: `md` = 48rem). Se mantienen ambos sin cambios y la barra inferior y el header móvil se alinean con ese mismo corte (`md:hidden`).

Las tablets se usan a dos manos, así que el sidebar es adecuado desde 768px; la barra inferior se reserva para el teléfono.

*Alternativa descartada:* subir el corte a 1024px para que las tablets en vertical usen la barra inferior. Exigía editar el componente generado de shadcn (clases `md:` → `lg:`) y el hook, y cambiaba la vista del calendario en tablets, sin beneficio para un uso a dos manos.

### D2 - La barra inferior y el header se muestran por CSS, no por `useIsMobile`

`BottomNav` y `MobileHeader` usan `md:hidden`. `useIsMobile` arranca en `false` antes del primer efecto; si se usara para renderizarlos, en móvil habría un parpadeo con el layout de escritorio. Con CSS, el primer pintado ya es correcto. El sidebar sigue usando `useIsMobile` internamente (comportamiento existente de shadcn): en móvil renderiza un `Sheet` cerrado que nadie abre, así que no hay impacto visible.

### D3 - Fuente de datos única con ubicación móvil explícita

`NavSection` gana un campo `mobile?: "bottom" | "account"`:
- `bottom`: Home, Search, Saved, Calendar, Downloads.
- `account`: Storage, Profile.
- Sin valor: no aparece en móvil (Franchises, deshabilitado).

`BottomNav` y `AccountMenu` filtran la data aplanada por ese campo. El sidebar sigue usando los grupos tal como están. Así, agregar una sección obliga a decidir su lugar en móvil en el mismo sitio.

*Alternativa descartada:* listas separadas para móvil. Se desincronizan.

### D4 - Estado activo con `Link` de TanStack Router

En la barra inferior, `Link` con `activeProps` (clase de resaltado). TanStack ya agrega `aria-current="page"` al link activo. En el sidebar, `SidebarMenuButton` expone `isActive` (`data-active`): se calcula con `useMatchRoute` o con `activeProps` sobre el `Link` hijo, usando `data-status="active"` que TanStack pone en el link. Se elige lo que requiera menos código sin tocar `sidebar.tsx` más allá del breakpoint.

Para el detalle de un anime (`/anime/$slug`) ningún ítem queda activo; es aceptable.

### D5 - Menú de cuenta con `DropdownMenu` y diálogo de logout extraído

`AccountMenu` usa `components/ui/dropdown-menu.tsx` (ya existe). El diálogo de confirmación de `NavUser` se extrae a un componente `LogoutDialog` controlado (`open`, `onOpenChange`) y lo usan tanto `NavUser` como `AccountMenu`. El dropdown se cierra antes de abrir el diálogo para evitar dos capas modales con foco compitiendo.

### D6 - Shell autenticado único

Nuevo `AppShell({ children })` en `features/root/components/` con `SidebarProvider` + `TooltipProvider` + `AppSidebar` + `SidebarInset` (`MobileHeader`, `children`, `BottomNav`). `_app/route.tsx` lo usa con `<Outlet/>` y `NotFound` con `<NotFoundContent/>`.

### D7 - Área segura y espacio reservado

- `index.html`: `viewport-fit=cover` para que `env(safe-area-inset-bottom)` tenga valor en iOS.
- `BottomNav`: `fixed inset-x-0 bottom-0`, alto de ítems de 4rem (mínimo táctil de 44px holgado) más `padding-bottom: env(safe-area-inset-bottom)`.
- El contenedor de contenido en `AppShell` aplica `padding-bottom: calc(4rem + env(safe-area-inset-bottom))` bajo `md` y `0` desde `md`.
- Con `viewport-fit=cover`, el header superior queda bajo la barra de estado solo en modo standalone, que no se usa (no hay PWA); en Safari normal no cambia nada.

## Risks / Trade-offs

- [La barra/header (CSS `md:hidden`) y el sidebar (`useIsMobile`) usan mecanismos distintos para el mismo corte] → Ambos valen 768px por defecto; si alguna vez se cambia uno, hay que cambiar el otro. Se deja un comentario junto a `BottomNav` apuntando a `MOBILE_BREAKPOINT`.
- [Diálogos y sheets fijos al fondo (p. ej. `Sheet` side="bottom" o toasts de `sonner`) podrían quedar debajo de la barra] → La barra usa un `z-index` menor que los overlays de Radix; los toasts se verifican y, si se superponen, se les agrega offset inferior en móvil.
- [Rutas con alto completo (`h-svh`/`h-screen`) quedarían cortadas por el padding] → Verificar cada página del `_app` en 390px y 820px.

## Migration Plan

Cambio solo de frontend, sin datos. Se despliega con el release normal (bump de `VERSION`). Rollback: revertir el PR.

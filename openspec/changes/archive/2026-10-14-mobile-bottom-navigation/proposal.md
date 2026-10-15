## Why

En el teléfono, la navegación de la app autenticada depende de un sidebar que se abre como cajón lateral desde un botón hamburguesa en la esquina superior izquierda: cada cambio de sección cuesta dos taps, tapa el contenido y obliga a estirar el pulgar a la zona menos accesible de la pantalla.

## What Changes

- Bajo 768px (el breakpoint móvil por defecto de shadcn, que la app ya usa) la navegación principal pasa a una **barra inferior fija** con las 5 secciones de anime: Home, Search, Saved, Calendar y Downloads, con la sección activa resaltada.
- El header móvil reemplaza el botón hamburguesa por un **menú de cuenta** (avatar) a la derecha, con: usuario y rol, Profile, Storage y Sign out (con la confirmación existente). Franchises, hoy deshabilitado, no aparece en móvil.
- El sidebar deja de existir como cajón en móvil; desde 768px se muestra igual que hoy (incluidas las tablets, pensadas para uso a dos manos) y ahora marca la sección activa.
- La barra inferior respeta el área segura inferior del dispositivo y el contenido reserva espacio para que la barra nunca tape lo último de la página.
- El armado del shell autenticado (sidebar, header, barra) se unifica para la app y la página 404 autenticada.

Fuera de alcance (change posterior): adaptación de tablas y filtros (Downloads, Episodes, Storage, Saved) a móvil.

## Capabilities

### New Capabilities
- `app-navigation`: navegación de la aplicación autenticada según el ancho de pantalla: sidebar en tablet y escritorio, barra inferior y menú de cuenta en teléfono, umbral de corte, indicación de sección activa y área segura.

### Modified Capabilities
<!-- Ninguna: no hay specs existentes sobre navegación o layout. -->

## Impact

- Frontend únicamente: `frontend/src/routes/_app/route.tsx`, `frontend/src/components/not-found.tsx`, `frontend/src/features/root/` (sidebar, header móvil, datos de navegación, nueva barra inferior y menú de cuenta), `frontend/index.html` (`viewport-fit=cover`).
- Sin cambios en `use-mobile.ts`, en el componente `sidebar.tsx` de shadcn ni en el calendario: se conserva el breakpoint por defecto.
- Sin cambios de backend, worker ni API. Sin dependencias nuevas.
- Release: bump de `VERSION` en el mismo PR.

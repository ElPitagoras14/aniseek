## 1. Prerrequisito

- [ ] 1.1 Confirmar que `add-backend-testing` está aplicado y que sus pruebas de atomicidad pasan contra la implementación actual con `databases`. Sin esa red, el modo de fallo dominante de este change no es detectable

## 2. Reescribir el módulo de acceso

- [ ] 2.1 Reemplazar en `backend/src/database/client.py` el objeto de `databases` por un engine asincrónico de SQLAlchemy construido sobre la misma `DB_URL`
- [ ] 2.2 Declarar explícitamente los límites del pool traduciendo los actuales: 5 conexiones permanentes y un techo total de 20, repartido entre permanentes y desbordamiento. No adoptar los valores por defecto de SQLAlchemy
- [ ] 2.3 Escribir las cinco funciones auxiliares —`execute`, `execute_many`, `fetch_one`, `fetch_all`, `fetch_val`— con la conexión como primer parámetro, envolviendo el SQL y normalizando la forma de los resultados como los repositorios ya asumen
- [ ] 2.4 Escribir el ciclo de vida: al arrancar, un `SELECT 1` explícito que falle ruidosamente si la base no responde; al cerrar, liberar el engine
- [ ] 2.5 Eliminar `get_pool_stats` y quitarla de las exportaciones de `backend/src/database/__init__.py`; está definida y exportada pero no se consume en ningún lado
- [ ] 2.6 Ajustar `backend/src/main.py` a las nuevas funciones de ciclo de vida

## 3. Migrar los paquetes, de menor a mayor

Cada paso deja su paquete consistente: la firma de sus funciones de acceso y sus llamadores se actualizan juntos.

- [ ] 3.1 `packages/auth/` — 4 usos, sin transacciones. Es el paquete más chico: sirve para fijar el patrón antes de aplicarlo en los grandes
- [ ] 3.2 `packages/users/` — 14 usos, sin transacciones
- [ ] 3.3 `packages/franchises/` — 7 usos en el repositorio, más el bloque de transacción de `service.py:53`. Primer paquete con transacción: el servicio pasa a abrir la conexión y propagarla
- [ ] 3.4 `packages/animes/` — 19 usos, más las transacciones de `add_new_anime` y `update_anime_info`
- [ ] 3.5 `packages/episodes/` — 23 usos, más las transacciones de `download_anime_episode_controller`, `download_anime_episode_bulk_controller` y `delete_anime_storage_controller`
- [ ] 3.6 Confirmar por búsqueda que no queda ninguna referencia al objeto global de `databases` en `backend/src/`

## 4. Resolver el sembrado del usuario administrador

- [ ] 4.1 `backend/src/main.py` siembra el usuario `admin` durante el arranque usando el objeto global. Definir si abre su propia conexión o la recibe del ciclo de vida, e implementarlo
- [ ] 4.2 Verificar que el sembrado sigue funcionando con el engine perezoso, que ahora abre la primera conexión al ejecutar la consulta y no al construirse

## 5. Dependencias

- [ ] 5.1 En `backend/pyproject.toml`: quitar `databases[asyncpg]`, agregar `sqlalchemy` como dependencia directa y el driver psycopg3
- [ ] 5.2 En `worker/pyproject.toml`: quitar `psycopg2-binary`, agregar el driver psycopg3. El código del worker no cambia
- [ ] 5.3 Ejecutar `uv lock` en `backend/` y en `worker/` para mantener los `uv.lock` sincronizados; un lock desfasado rompe el build de Docker, que instala con `--locked`

## 6. Configuración

- [ ] 6.1 Cambiar el esquema de `DB_URL` a `postgresql+psycopg://` en `.env.example`
- [ ] 6.2 Hacer lo mismo en `compose.yaml` y en `compose.dev.yaml`, con el mismo valor para la API y para el worker
- [ ] 6.3 Confirmar que ningún servicio traduce ni transforma la cadena antes de usarla

## 7. Verificar

- [ ] 7.1 Ejecutar la suite de pruebas y confirmar que las siete siguen en verde. Es la comprobación central del change
- [ ] 7.2 Confirmar que las escrituras de cada transacción se ejecutan sobre la conexión que la abrió, y no sobre otra. Es el error que sobrevive al análisis de tipos: pasar una conexión, pero la equivocada
- [ ] 7.3 Ejercitar las rutas del backend que usan `execute_many` e `ON CONFLICT`, donde psycopg3 y asyncpg podrían diferir
- [ ] 7.4 Ejercitar las consultas que devuelven `COUNT`, por la misma razón
- [ ] 7.5 Levantar el stack completo y confirmar que el backend arranca, autentica y responde
- [ ] 7.6 Encolar una descarga y una reordenación de franquicia, y confirmar que el worker consulta correctamente contra psycopg3. Su verificación tiene que ser funcional: no cambió una sola línea de su código
- [ ] 7.7 Confirmar que el backend no arranca si la base no responde, deteniendo el contenedor de la base y levantando la API

## 8. Cerrar

- [ ] 8.1 Anotar en las notas de la versión que `DB_URL` cambia de esquema, y que la variable y las imágenes deben desplegarse juntas: una imagen anterior con el esquema nuevo no arranca, y una imagen nueva con el esquema anterior tampoco
- [ ] 8.2 Subir la versión de los servicios siguiendo la convención del repositorio de versionarlos en conjunto, ejecutando `uv lock` en cada directorio cuyo `pyproject.toml` cambie

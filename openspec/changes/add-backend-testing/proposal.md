## Why

El repositorio no tiene ninguna prueba automatizada. No existen archivos de test en `backend/` ni en `worker/`, no hay runner declarado, y los grupos de dependencias de desarrollo del backend contienen únicamente `isort` y `ruff`.

Eso no era urgente mientras los changes fueran acotados, pero deja de serlo con `unify-database-access`. Ese change reemplaza la propagación implícita de la conexión —hoy provista por `databases`— por el paso explícito que recomienda SQLAlchemy, y eso implica alrededor de 113 ediciones mecánicas: sumar el parámetro de conexión a unas 40 funciones de repositorio y propagarlo desde sus 73 llamadores.

El riesgo de esas ediciones no es que fallen, sino cómo fallan. Pasar una conexión distinta de la que abrió la transacción en curso no produce error: las consultas se ejecutan, la aplicación responde igual, y la atomicidad se pierde en silencio. Recién se manifiesta cuando algo falla a mitad de una operación de varias sentencias y quedan escrituras parciales confirmadas. Hay 6 caminos así en el backend.

Esa propiedad —que ante un fallo intermedio ninguna escritura de la transacción persista— no se puede verificar leyendo el código ni usando la aplicación. Solo se comprueba provocando el fallo y mirando la base después.

**Y el orden importa: las pruebas tienen que existir antes de la migración.** Escritas después, no verificarían el comportamiento previo sino que consagrarían el que la migración produjo, que es exactamente lo contrario de una red de seguridad.

## What Changes

- Se incorpora al backend una infraestructura de pruebas: runner, soporte para código asincrónico y las dependencias correspondientes en el grupo de desarrollo, junto con la configuración necesaria para que las pruebas encuentren los módulos de `src/`.
- Se agrega una base de datos de prueba **real de PostgreSQL**, efímera y separada de la de desarrollo. Las consultas del backend usan `ON CONFLICT ... DO UPDATE`, `EXCLUDED`, `CURRENT_TIMESTAMP` y tipos `UUID`; una base sustituta como SQLite no reproduce esa semántica y volvería inútiles las pruebas para el propósito que las motiva.
- Se define una estrategia de aislamiento entre pruebas que **no** envuelva cada prueba en una transacción. Es el patrón habitual, pero acá es inaplicable: si la prueba abre una transacción, la del código bajo prueba se degrada a un savepoint y deja de verificarse lo que interesa.
- Se escriben pruebas para los 6 caminos transaccionales del backend, contra la implementación actual con `databases`. Cada una provoca un fallo en medio de la transacción y comprueba que ninguna de sus escrituras persistió.
- Se documenta cómo ejecutar las pruebas, para que el procedimiento no viva solo en la memoria de quien las escribió.

Non-goals: no se busca cobertura amplia ni se escriben pruebas de rutas, de autenticación ni del scraping; este change establece el andamiaje y protege exactamente la propiedad que `unify-database-access` pone en riesgo. No se agregan pruebas al worker ni al frontend. No se modifica código de producción: las pruebas se escriben contra el comportamiento existente sin alterarlo.

## Capabilities

### New Capabilities

- `backend-testing`: cómo se verifica automáticamente el comportamiento del backend — qué se ejecuta, contra qué base de datos, cómo se aísla una prueba de otra, y qué garantías debe poder comprobar una prueba que no son observables leyendo el código.

### Modified Capabilities

<!-- Ninguna. `database-access` describe cómo se consulta la base; esta capability describe cómo se verifica ese comportamiento. -->

## Impact

- `backend/pyproject.toml` — se agregan las dependencias de prueba al grupo de desarrollo y la configuración del runner
- `backend/tests/` — nuevo: configuración compartida, utilidades de base de datos de prueba y las pruebas de los caminos transaccionales
- `README.md` — se documenta cómo ejecutar las pruebas
- Sin cambios en `backend/src/`, `worker/` ni `frontend/`

Relación con otros changes:

- **Bloquea a `unify-database-access`.** Ese change no debería aplicarse sin esta red, porque su modo de fallo dominante es silencioso.
- **Interactúa con `adopt-dbmate`.** La base de prueba necesita un esquema, y hoy la única fuente es `postgres/init.sql`. Si `adopt-dbmate` ya está aplicado, el esquema de prueba se construye con las migraciones, que es lo correcto: la base contra la que se prueba se crea por el mismo camino que la de producción. Si no lo está, se parte de `init.sql` y se ajusta después. Ninguno de los dos bloquea al otro, pero aplicar `adopt-dbmate` primero evita rehacer esa parte.

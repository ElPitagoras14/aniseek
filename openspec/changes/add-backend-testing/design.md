## Context

El backend no tiene pruebas ni infraestructura para ejecutarlas. Sus dependencias de desarrollo son `isort` y `ruff`; no hay runner, configuración ni directorio de tests.

Cuatro rasgos del código condicionan cualquier diseño de pruebas:

- **La configuración se resuelve al importar.** `general_settings`, `database_settings`, `auth_settings` y el propio objeto de base de datos se construyen en el cuerpo de sus módulos. `DatabaseSettings` exige `DB_URL` y `GeneralSettings` exige `SECRET_KEY`, `ALGORITHM` y `REDIS_URL`, ninguno con valor por defecto. Importar cualquier módulo de la aplicación sin esas variables falla, y el objeto de base de datos queda ligado a la URL vigente en ese instante.
- **La raíz de importación es `src/`.** Los módulos se importan como `from database import ...` y `from config import ...`, no como paquete anidado.
- **Las consultas son específicas de PostgreSQL.** `ON CONFLICT ... DO UPDATE`, `EXCLUDED`, `CURRENT_TIMESTAMP` y columnas `UUID` aparecen en los repositorios.
- **Hay datos de referencia sin los cuales la aplicación no funciona.** `role_types`, `related_types` y `avatars` se siembran junto con el esquema.

La propiedad que hay que poder verificar es una sola: que ante un fallo a mitad de una transacción de varias sentencias, ninguna de sus escrituras persista.

## Goals / Non-Goals

**Goals:**

- Poder ejecutar pruebas del backend con un solo comando, sin pasos manuales previos.
- Verificar la atomicidad de los 6 caminos transaccionales contra PostgreSQL real.
- Que las pruebas queden aisladas entre sí sin recurrir a un mecanismo que invalide lo que se está verificando.
- Dejar el andamiaje listo para que agregar una prueba nueva no exija volver a resolver la infraestructura.

**Non-Goals:**

- Cobertura amplia, pruebas de rutas, de autenticación o del scraping.
- Pruebas del worker o del frontend.
- Modificar código de producción. Las pruebas se escriben contra el comportamiento existente.

## Decisions

### D1 — pytest con soporte asincrónico en modo automático

El backend es asincrónico de punta a punta. Se adopta pytest con el complemento de asincronía configurado en modo automático, de manera que las funciones de prueba `async def` se ejecuten sin decorar cada una.

Se elige el complemento basado en asyncio y no el genérico de múltiples backends porque el código usa asyncio directamente y no hay intención de soportar otro runtime; el genérico obligaría a declarar el backend en cada prueba sin aportar nada.

### D2 — Una base de datos PostgreSQL efímera, levantada por la propia suite

Las pruebas levantan un contenedor de PostgreSQL de la misma versión que producción, lo usan durante la sesión y lo descartan al terminar. No dependen de que el entorno de desarrollo esté corriendo ni de una base preexistente.

El motivo es de uso diario: una suite que exige levantar servicios antes de correrla se ejecuta menos, y una suite que se ejecuta menos no protege nada. El proyecto ya requiere Docker para todo lo demás, así que no se agrega un requisito nuevo.

*Alternativa considerada:* agregar un servicio de base de datos de prueba a `compose.dev.yaml`. Evita una dependencia de desarrollo, pero convierte "correr las pruebas" en dos pasos y deja la base viva entre ejecuciones, con el riesgo de que el estado de una sesión contamine la siguiente.

*Alternativa descartada:* una base sustituta en memoria. No reproduce `ON CONFLICT ... DO UPDATE`, `EXCLUDED` ni los tipos `UUID`, de modo que las pruebas pasarían sin verificar el comportamiento real — el peor resultado posible para una suite cuyo propósito es dar confianza en una migración.

### D3 — El esquema de prueba se crea por el mismo camino que el de producción

La base efímera se construye aplicando el mismo artefacto que construye la de producción, sea `postgres/init.sql` hoy o las migraciones una vez aplicado `adopt-dbmate`.

La provisión se aísla en un único punto para que ese cambio de fuente sea una modificación localizada y no una reescritura de los fixtures. Probar contra un esquema construido de otra manera que el real invalidaría silenciosamente las pruebas.

### D4 — El aislamiento entre pruebas es por truncado selectivo, no por transacción envolvente

El patrón habitual —abrir una transacción antes de cada prueba y revertirla después— **es inaplicable acá**. Si la prueba mantiene una transacción abierta, la que abre el código bajo prueba se convierte en un savepoint anidado, y revertirla deja de demostrar lo que interesa demostrar. Adoptarlo por costumbre produciría una suite que parece verificar la atomicidad sin verificarla.

En su lugar, entre pruebas se truncan las tablas mutables y se conservan las de referencia. La lista de tablas a truncar se deriva del esquema en tiempo de ejecución, excluyendo una lista explícita y corta de tablas preservadas: las de referencia y la de control de migraciones. Así, una tabla nueva queda cubierta automáticamente —que es lo correcto— y lo que se preserva está declarado a la vista.

### D5 — La configuración se fija antes de que se importe la aplicación

Como la configuración se resuelve al importar y el objeto de base de datos queda ligado a la URL de ese instante, la base efímera tiene que existir y sus variables de entorno tienen que estar puestas **antes** de que se importe cualquier módulo de la aplicación.

Eso descarta resolverlo con un fixture corriente: para cuando los fixtures se ejecutan, los módulos de prueba ya fueron importados y con ellos los de la aplicación. La provisión se hace por lo tanto en el enganche de configuración de pytest, que corre antes de la recolección.

Es una consecuencia directa de cómo está escrita la aplicación, no una preferencia. Si en el futuro la configuración pasara a resolverse de forma diferida, esta restricción desaparecería.

### D6 — El fallo se provoca sustituyendo un colaborador, no violando una restricción

Cada prueba de atomicidad necesita que algo falle en medio de la transacción. Se hace sustituyendo una de las funciones que la transacción invoca después de su primera escritura, para que lance una excepción.

*Alternativa considerada:* provocar un error real de base de datos violando una restricción. Es más realista, pero ata la prueba a una restricción concreta del esquema: cambiarla rompería la prueba por un motivo que no tiene relación con lo que verifica. La sustitución expresa la intención directamente —"algo falla a mitad"— y sobrevive a los cambios de esquema.

Se verificó que los 6 bloques invocan a sus repositorios por atributo de módulo —`repository.insert_user_episode_download(...)`—, de modo que la sustitución es posible en todos.

Cada prueba verifica que la escritura previa al fallo **no** esté en la base. Verificar además que la excepción se propague vale para 5 de los 6 caminos, **pero no para el de descarga en lote**: ahí la transacción está dentro de un `try/except` que captura la excepción, registra el episodio como fallido y continúa con el siguiente. Su prueba comprueba que el bucle sigue, que ese episodio queda marcado como fallido y que ninguna de sus escrituras persistió; que la excepción no salga es el comportamiento correcto, no un defecto.

Además, los dos caminos de descarga encolan en Dramatiq —`download_anime_episode.send(...)`— antes de abrir la transacción. Ese envío también se sustituye: de lo contrario las pruebas dependerían de un Redis disponible y publicarían mensajes reales.

### D7 — Las pruebas viven en `backend/tests/`, con `src` declarado raíz de importación

El directorio de pruebas se ubica junto a `src/`, no dentro. La configuración del runner declara `src` como raíz de importación, de modo que las pruebas importen los módulos exactamente igual que la aplicación —`from database import ...`— y no se introduzca una segunda forma de referirse al mismo código.

La ubicación tiene además una consecuencia práctica que la refuerza: el `Dockerfile` del backend copia `src` y nada más, y resuelve dependencias con `--no-dev`. Con las pruebas fuera de `src/` y sus dependencias en el grupo de desarrollo, **ninguna de las dos cosas llega a la imagen de producción por construcción**, sin necesidad de agregar exclusiones al `.dockerignore`. Ubicarlas dentro de `src/` las habría empaquetado y desplegado.

### D8 — Los datos de cada prueba se construyen en la prueba

Se agregan funciones auxiliares que crean las filas mínimas de cada escenario —un usuario, un anime, sus episodios— y cada prueba invoca las que necesita.

Es consecuencia directa de D4: con truncado entre pruebas, un conjunto sembrado de antemano tendría que recrearse igual antes de cada una, con lo que "sembrar una vez" se vuelve un constructor disfrazado. Hacerlo explícito evita además el acoplamiento típico de los datos compartidos, donde una prueba depende sin saberlo de una fila que otra dio por sentada.

## Risks / Trade-offs

- **Las pruebas fijan el comportamiento actual, incluidas sus rarezas.** → `update_anime_info` realiza un scraping de red con la transacción abierta. La prueba tendrá que sustituir ese scraping, y al hacerlo consagra la estructura actual. Es el precio de una red de seguridad escrita antes de la migración: protege contra regresiones, no contra decisiones de diseño discutibles. Corregir ese alcance excesivo es un change aparte, y esta suite lo hará más seguro.

- **Se agrega una dependencia de desarrollo para levantar la base.** → Es superficie nueva que hay que mantener. Se acepta a cambio de que la suite se ejecute con un solo comando; la alternativa de un servicio en compose no tiene la dependencia pero sí el paso manual.

- **La primera ejecución es lenta y exige Docker corriendo.** → Descargar o iniciar la imagen agrega segundos a la primera corrida de la sesión. Las siguientes reutilizan el mismo contenedor. En una máquina sin Docker activo la suite no corre en absoluto, lo cual es aceptable en un proyecto que ya lo requiere para todo lo demás.

- **La lista de tablas preservadas puede quedar desactualizada.** → Si se agregan datos de referencia nuevos en una tabla nueva, el truncado los borraría y las pruebas fallarían. El fallo es ruidoso y la corrección es una línea, pero conviene que la lista esté junto a la definición del esquema en la cabeza de quien lo modifique.

- **Truncar entre pruebas es más lento que revertir una transacción.** → Con una decena de pruebas la diferencia es irrelevante. Si la suite creciera mucho, convendría revisarlo, pero no a costa de D4.

## Migration Plan

1. Agregar las dependencias de prueba al grupo de desarrollo del backend y la configuración del runner, incluida la raíz de importación de D7.
2. Escribir la provisión de la base efímera y el enganche que fija las variables de entorno antes de la recolección (D2, D5).
3. Escribir la creación del esquema desde la fuente canónica vigente, aislada en un punto único (D3).
4. Escribir el truncado selectivo entre pruebas con su lista explícita de tablas preservadas (D4).
5. Verificar el andamiaje con una prueba trivial que escriba y lea una fila, y confirmar que dos pruebas consecutivas no se ven entre sí.
6. Escribir las 6 pruebas de atomicidad, una por camino transaccional (D6).
7. Confirmar que las 6 pasan contra la implementación actual con `databases`. Si alguna falla, el hallazgo es un defecto preexistente y hay que tratarlo antes de seguir.
8. Documentar en el `README.md` cómo ejecutar la suite.

**Rollback:** revertir el commit. No se toca código de producción, así que quitar las pruebas no afecta al servicio.

## Open Questions

Ninguna abierta. Las tres se resolvieron y sus respuestas están incorporadas en D6 y en las decisiones siguientes:

- **¿Los puntos a sustituir son alcanzables?** Sí, verificado en los 6 caminos: todos invocan a sus repositorios por atributo de módulo. La revisión además destapó dos particularidades que ahora forman parte de D6: el camino de descarga en lote captura la excepción en vez de propagarla, y los dos caminos de descarga encolan en Dramatiq antes de la transacción.
- **¿Cuántos contenedores?** Uno por ejecución completa de la suite, reutilizado entre pruebas — es lo que D4 asume al truncar. Se descarta reutilizarlo entre ejecuciones distintas: ahorraría el arranque, pero hace que el resultado dependa de lo que dejó la corrida anterior, y una suite cuyo propósito es dar confianza no puede pagar ese precio. Si el arranque llegara a molestar, la reutilización es la primera palanca a considerar.
- **¿Datos de prueba sembrados una vez o construidos por prueba?** Construidos por prueba, y la decisión la fuerza D4: el truncado entre pruebas borraría cualquier conjunto sembrado de antemano, así que "sembrar una vez" tendría que volverse "sembrar antes de cada prueba" — que es exactamente un constructor, pero menos explícito. Cada prueba declara los datos que necesita.


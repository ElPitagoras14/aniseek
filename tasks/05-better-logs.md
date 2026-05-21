# Mejorar los logs

Carpeta de contexto @backend/src

En los endpoints que utilicen `logger` deben usar `loguru` y no `print` o `sys.stdout.write`. El log solo va a existir en consola y no en archivos. El nivel del log se obtiene de la variable de entorno `LOG_LEVEL`.

Asegurar que todos los archivos `.py` usen `loguru`.

El mensaje de log debe ser claro y conciso. Debe incluir información relevante del momento en el código que generó el log. No debe contener información sensible (passwords, tokens, etc.).

Debes usar correctamente los niveles de log.

Ya tienes bindeado actualmente el `uuid` de la transaction y el `usuario` en cada log.

Escribe los resultados obtenidos a este documento.

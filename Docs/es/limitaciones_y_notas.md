# Limitaciones y notas

## Ajustes no persistentes
Los ajustes se restablecen a los valores predeterminados en cada inicio.

## Sin modo por lotes
Un archivo a la vez.

## Calidad de la traducción
Helsinki-NLP puede presentar imprecisiones. Se recomienda revisión manual.

## Sin verificación automática de tiempos
El texto traducido puede ser más largo o más corto que el original. Es necesaria la edición manual del SRT.

## Transcripción: detección automática del idioma
Whisper puede equivocarse con audio ruidoso. Especifica el idioma manualmente si es necesario.

## Transcripción: gestión de memoria
Los archivos largos pueden provocar ralentizaciones en sistemas con poca RAM.

## WhisperX no integrado
El entorno está preparado, pero no está integrado en el pipeline principal.

## Subtítulos no disponibles
La opción de menú está presente, pero no está implementada.

## Proveedores TTS adicionales no conectados
Solo Azure y Google. OpenAI y ElevenLabs están planificados.

## Traducción por pivote no disponible
Se requiere un par directo. La traducción por pivote está planificada.

## Portabilidad limitada
Mover el proyecto requiere reconstruir el entorno virtual.

## Procesamiento secuencial
No hay paralelización disponible.

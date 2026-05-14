# Guía de uso

Esta guía describe el flujo operativo de DubbingToolkit, desde la preparación de archivos de entrada hasta el audio doblado final.

---

## Iniciar el proyecto

Haz doble clic en `StartDubbing.bat`. El proyecto se inicia y presenta el menú de gestión de proyectos.

---

## Crear y seleccionar un proyecto

Desde la pantalla principal, selecciona "Gestión de proyectos" (opción 0) y crea un nuevo proyecto. Cada proyecto es un espacio de trabajo aislado para un vídeo específico.

Una vez creado, el proyecto se establece como activo y permanece disponible para operaciones posteriores.

---

## Flujo de trabajo

El proceso consta de 4 fases. Cada fase puede ejecutarse individualmente o como parte del flujo completo.

| Fase | Operación | Carpeta de salida |
|---|---|---|
| 1 | Extracción de audio | `Workspace/projects/{nombre}/audio_extraction/current/` |
| 2 | Transcripción | `Workspace/projects/{nombre}/transcripts/current/` |
| 3 | Traducción | `Workspace/projects/{nombre}/translated/current/` |
| 4 | Síntesis TTS | `Workspace/projects/{nombre}/dubbed/current/` |

> **Importante:** se recomienda revisión manual tras la transcripción y la traducción. Las correcciones permiten mejorar la calidad del audio final.

---

## Preparación de los archivos de entrada

### Entrada de vídeo

Durante la extracción de audio, el sistema presenta un diálogo de importación que permite:
1. Usar el vídeo desde una ubicación externa (mantiene la ruta original)
2. Copiar el vídeo al proyecto (`Workspace/projects/{nombre}/video_input/`)
3. Mover el vídeo al proyecto

Formatos soportados: aquellos manejados por ffmpeg (mp4, mkv, avi, mov, etc.).

### Audio directo

Si ya tienes audio extraído, durante la transcripción puedes seleccionar manualmente un archivo de audio desde la carpeta `Workspace/projects/{nombre}/audio_input/` o desde una ubicación externa. En este caso, la Fase 1 puede omitirse.

---

## Fase 1 — Extracción de audio

El sistema extrae las pistas de audio del vídeo mediante ffmpeg. Todos los archivos de audio extraído se guardan en `Workspace/projects/{nombre}/audio_extraction/current/` con nombres `track_01.wav`, `track_02.wav`, etc.

Para cada pista se genera automáticamente un archivo de metadatos (`track_XX_metadata.json`) con información sobre codec, frecuencia de muestreo, duración y otras propiedades.

---

## Fase 2 — Transcripción

El audio se transcribe en formato SRT. El idioma hablado se detecta automáticamente y puede cambiarse desde el menú antes de iniciar la transcripción. El resultado se guarda en `Workspace/projects/{nombre}/transcripts/current/`.

> **Consejo:** revisa y corrige el texto transcrito antes de traducir. Los errores en esta fase se propagan a las fases posteriores.

---

## Fase 3 — Traducción

El archivo SRT transcrito se traduce al idioma de destino. La traducción ocurre completamente en local. Los modelos necesarios se descargan automáticamente en la primera ejecución para cada par de idiomas. El resultado se guarda en `Workspace/projects/{nombre}/translated/current/`.

Si el par de idiomas directo no está disponible, la traducción mediante inglés como idioma intermedio está planeada para el futuro.

> **Consejo:** revisa el texto traducido antes de iniciar la síntesis. Las correcciones manuales permiten gestionar desajustes de sincronización.

---

## Fase 4 — TTS

El texto traducido se sintetiza segmento por segmento mediante el proveedor TTS seleccionado. Los segmentos se fusionan en el archivo de audio final, guardado en `Workspace/projects/{nombre}/dubbed/current/`.

### Proveedores TTS

El sistema actualmente soporta dos proveedores:

- **Azure Cognitive Services Speech** — servicio TTS en la nube de Microsoft
- **Google Cloud Text-to-Speech** — servicio TTS en la nube de Google

El proveedor y la voz se seleccionan directamente desde el menú TTS. El sistema incluye una función dedicada para escuchar muestras de voz disponibles antes de iniciar la síntesis.

### Monitoreo de costos

Cuando se inicia el módulo TTS, se muestra automáticamente una estimación de uso. Para verificar el consumo real, consulta directamente el panel de control de tu proveedor.

---

## Idioma de la interfaz

El idioma de la interfaz se selecciona al inicio y puede cambiarse en cualquier momento desde el menú de configuración sin reiniciar el proyecto.

---

## Gestión de proyectos

### Duplicación

Puedes duplicar un proyecto existente para crear una copia con un nuevo nombre. Útil para probar variaciones de la misma fuente.

### Renombrar

Un proyecto puede renombrarse en cualquier momento desde la gestión de proyectos. Si el proyecto está activo, el puntero activo se actualiza automáticamente.

### Eliminación

Un proyecto puede eliminarse. Si la configuración `use_trash` está habilitada, el proyecto se mueve a la Papelera; de lo contrario se elimina permanentemente.

### Abrir carpeta

Puedes abrir la carpeta de un proyecto directamente en Explorer para inspeccionar manualmente los archivos generados.

---

## Consejos operativos

- Usa nombres cortos de proyecto y archivo sin espacios ni caracteres especiales para evitar problemas de rutas.
- Los archivos en `Workspace/projects/{nombre}/video_input/` nunca se modifican por el sistema.
- Cada fase genera metadatos (archivos `.json` o `_info.txt`): útiles para hacer seguimiento del progreso o diagnosticar problemas.
- Si se interrumpe el proceso, puedes reanudar desde la siguiente fase usando los archivos en las carpetas de salida intermedia.
- Los archivos procesados en cada fase se archivan automáticamente en la carpeta `archive/` de esa fase para preservar el historial.

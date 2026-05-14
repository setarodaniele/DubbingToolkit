# DubbingToolkit

> ⚠️ **Advertencia**: Esta documentación ha sido traducida automáticamente y puede contener errores o imprecisiones. Para una comprensión detallada, consulte la versión en [inglés](../en/README.md).

**DubbingToolkit** es un sistema de doblaje híbrido Python + PowerShell para transcribir, traducir y re-sintetizar contenido de audio/vídeo en múltiples idiomas, utilizando motores TTS profesionales (Azure, Google) y modelos de transcripción locales (Whisper).

## Índice de documentación

| Archivo | Contenido |
|---|---|
| [README.md](README.md) | Esta página — visión general |
| [instalacion.md](instalacion.md) | Requisitos, configuración inicial |
| [uso.md](uso.md) | Guía operativa y flujo de trabajo |
| [arquitectura.md](arquitectura.md) | Estructura del proyecto, módulos, convenciones |
| [faq.md](faq.md) | Preguntas frecuentes |
| [limitaciones_y_notas.md](limitaciones_y_notas.md) | Limitaciones actuales |
| [credenziali_azure.md](credenziali_azure.md) | Configuración de credenciales Azure |
| [credenziali_google.md](credenziali_google.md) | Configuración de credenciales Google |

## Qué hace

1. **Extracción de audio** — ffmpeg extrae el audio de los archivos de vídeo
2. **Transcripción** — Whisper transcribe a formato SRT
3. **Traducción** — modelos locales Helsinki-NLP, sin API externa
4. **TTS (Text-to-Speech)** — Azure TTS o Google TTS, segmento por segmento

## Idiomas de interfaz soportados

| Código | Idioma |
|---|---|
| `it` | Italiano |
| `en` | Inglés |
| `es` | Español |
| `de` | Alemán |
| `fr` | Francés |
| `pt` | Portugués |
| `ru` | Ruso |
| `zh` | Chino |

## Proveedores TTS

- **Azure Cognitive Services Speech**
- **Google Cloud Text-to-Speech**

Consulta [instalacion.md](instalacion.md) para la configuración.

## Punto de entrada

```
StartDubbing.bat
```

## Estado del proyecto

En desarrollo activo. Consulta [arquitectura.md](arquitectura.md) para el estado de los componentes.

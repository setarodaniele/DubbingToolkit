# Preguntas frecuentes y solución de problemas

## Inicio y entorno

**El proyecto no arranca con `StartDubbing.bat`.**
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**El entorno virtual está dañado o no se activa.**
Elimina la carpeta `venv/` y reinicia `StartDubbing.bat`.

**Error `[MISSING: key]` en la interfaz.**
Clave ausente en el archivo de localización activo. No es bloqueante.

## Credenciales y API

**Credenciales Azure no válidas.**
Verifica `subscription` y `region` en `credentials/azure_speech_credentials.json`.

**Credenciales Google no válidas.**
`credentials/google_speech_credentials.json` debe ser un JSON completo de cuenta de servicio de GCP con Cloud Text-to-Speech habilitado.

## Transcripción

**Resultados imprecisos o idioma incorrecto.**
Establece el idioma de origen manualmente desde el menú de idiomas.

**La transcripción es muy lenta.**

| Modelo | Velocidad | Calidad |
|---|---|---|
| `tiny` | Muy alta | Básica |
| `base` | Alta | Aceptable |
| `small` | Media | Buena |
| `medium` | Baja | Alta |
| `large` | Muy baja | Máxima |

**Error de memoria durante la transcripción.**
Divide el audio en segmentos más cortos.

## Traducción

**El par de idiomas deseado no está disponible.**
No todos los pares Helsinki-NLP están disponibles. La traducción por pivote está planificada.

**El texto traducido tiene errores.**
Helsinki-NLP puede tener imprecisiones con expresiones idiomáticas o términos técnicos.

## Síntesis TTS

**El audio tiene pausas antinaturales.**
Usa voces neuronales (Azure Neural, Google WaveNet).

**Salida silenciosa o con ruido.**
Verifica que `Translated/` contiene segmentos válidos y no vacíos.

**El monitoreo de uso no se actualiza.**
Haz una copia de seguridad y elimina `Billing/consumo_tts.json`.

## Archivos y carpetas

**No encuentro la salida.**
- `Audio_Extracted/`
- `Transcripts/`
- `Translated/`
- `Dubbed/<PROVIDER>/`

**Moví el proyecto y ahora no funciona.**
Elimina `venv/` y reinicia.

## Compilación y distribución

**Las credenciales de la API no están en el paquete de distribución.**
Comportamiento correcto. Introdúcelas manualmente tras la instalación.

## General

**¿Se puede usar sin conexión?**
Parcialmente. TTS requiere internet.

**¿Cómo agregar nuevos idiomas de interfaz?**
1. `locale/Active/<lang_code>.json`
2. `locale/System/languages.json`

**¿Procesamiento por lotes?**
No disponible. Un archivo a la vez. Planificado para el futuro.

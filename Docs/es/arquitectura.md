# Arquitectura y referencia técnica

## Estructura de carpetas

```
DubbingToolkit/
├── Audio_Extracted/
├── Audio_Input/
├── Billing/
├── core/
├── credentials/
├── Dubbed/
├── Installation/
├── installer/
├── locale/
│   ├── Active/
│   └── System/
├── Logs/
├── ps/
├── Repository/
├── Scripts/
│   └── maintenance/
├── Settings/
├── Subtitles/
├── Temp/
├── Tools/
├── Transcripts/
├── Translated/
├── venv/
├── Video_Input/
└── voices/
```

## Cadena de inicio

```
StartDubbing.bat
  └→ Scripts/Launcher.ps1
       └→ Scripts/Regista.py
```

## Pipeline

| Fase | Módulo | Entrada → Salida |
|---|---|---|
| 1 | `Scripts/estrai_tracce.py` | `Video_Input/` → `Audio_Extracted/<ts>/` |
| 2 | `Scripts/trascrivi_audio.py` | `Audio_Extracted/` → `Transcripts/<ts>/` |
| 3 | `Scripts/traduci_testo.py` | `Transcripts/` → `Translated/<ts>/` |
| 4 | `Scripts/tts_menu.py` | `Translated/` → `Dubbed/` |

## Módulos principales (`core/`)

- **`messages.py`** — mensajes localizados
```python
from core.messages import Messages
msg = Messages()
print(msg._("message_key"))
```
- **`credentials_manager.py`** — único lector autorizado de `credentials/`
- **`api_check.py`** — valida las credenciales antes del menú TTS
- **`ui_printer.py`** + **`ui_colors.py`** — formato de consola
- **`utils_tts.py`** — análisis SRT compartido
- **`file_selector.py`** — selección interactiva de archivos
- **`input_parsing.py`** — análisis de entrada del usuario

## Módulos principales de Scripts

- `Regista.py` — orquestador principal
- `estrai_tracce.py` — extracción de audio
- `trascrivi_audio.py` — transcripción
- `traduci_testo.py` — traducción
- `tts_menu.py` / `tts_dubbing.py` — pipeline TTS
- `tts_azure.py` / `tts_google.py` — backends TTS
- `tts_merge.py` — fusión de segmentos
- `tts_config_manager.py` — configuración TTS
- `info_manager.py` — project_info.json
- `settings_manager.py` — settings.json
- `monitoraggio_consumo.py` — seguimiento de uso TTS
- `menu_lingue.py` / `menu_lingue_tts.py` — menús de idioma
- `menu_voices.py` — selección de voz
- `backup_utils.py` — gestión de copias de seguridad

## Sistema de localización

```
locale/
├── Active/   it.json, en.json, es.json, de.json, fr.json, pt.json, ru.json, zh.json
└── System/   languages.json, whisper_languages.json
```

Reglas: todos los mensajes a través de `core/messages.py`. Todos los archivos de localización deben mantenerse sincronizados.

### Scripts de mantenimiento en `Scripts/maintenance/translation/`

| Script | Función |
|---|---|
| `LocaleKeyAnalyzer.ps1` | Análisis de claves ausentes |
| `LocaleTranslator.ps1` | Traducción automática |
| `Validate-LocaleJson.ps1` | Validación JSON |
| `Fix-LocaleDuplicates.ps1` | Corrección de duplicados |
| `Clean-LocaleUnusedKeys.ps1` | Eliminación de claves no utilizadas |
| `Extract-Placeholders.ps1` | Extracción de marcadores de posición |
| `Protect-Placeholders.ps1` | Protección de marcadores de posición |

## Configuración

```json
{
  "interface_lang": "it",
  "model": "small",
  "Transcript_Audio_Spoken_Lang": "it",
  "Translation_Target_Lang": "en",
  "Dubbing_Lang": "en"
}
```

| Campo | Descripción |
|---|---|
| `interface_lang` | Idioma de la interfaz |
| `model` | Modelo Whisper |
| `Transcript_Audio_Spoken_Lang` | Idioma del audio de origen |
| `Translation_Target_Lang` | Idioma de destino de la traducción |
| `Dubbing_Lang` | Idioma TTS |

## Gestión de voces TTS

| Archivo | Contenido |
|---|---|
| `voices_azure.json` | Voces Azure filtradas |
| `voices_azure_complete.json` | Catálogo completo de Azure |
| `voices_google.json` | Voces Google filtradas |
| `voices_google_complete.json` | Catálogo completo de Google |
| `voices_index.json` | Índice unificado |

## Sistema de compilación

```powershell
.\build.ps1              # menú interactivo
.\build.ps1 -Test        # compilación ligera
.\build.ps1 -Production  # compilación completa
.\build.ps1 -DryRun      # simulación
```

| Archivo | Función |
|---|---|
| `build_include.json` | Qué copiar |
| `build_exclude.json` | Lista negra global |
| `build_exclude_test.json` | Lista negra TEST |
| `build_protected.json` | Rutas protegidas |
| `build_empty_dirs.json` | Directorios vacíos |

## Convenciones

| Elemento | Convención |
|---|---|
| Carpetas | `minusculas_guion_bajo` |
| Módulos Python | `minusculas_guion_bajo.py` |
| Clases | `CamelCase` |
| Funciones/variables | `minusculas_guion_bajo` |
| Scripts de prueba | prefijo `test_` |

Estructura de scripts:
```
# 1. IMPORTS / DEPENDENCIES
# 2. CONFIGURATION
# 3. UTILITIES
# 4. CORE LOGIC
# 5. MAIN EXECUTION
```

## Estado de los componentes

| Componente | Estado |
|---|---|
| Extracción de audio | ✅ Operativo |
| Transcripción Whisper | ✅ Operativo |
| Traducción Helsinki-NLP | ✅ Operativo |
| Azure TTS | ✅ Operativo |
| Google TTS | ✅ Operativo |
| Interfaz multilingüe (8 idiomas) | ✅ Operativo |
| Monitoreo de uso TTS | ✅ Operativo |
| Sistema de compilación/empaquetado | ✅ Operativo |
| Subtítulos (opción de menú 5) | ⚠️ Stub |
| Segmentación avanzada | ⚠️ Placeholder |
| WhisperX | ⚠️ No integrado |
| TTS OpenAI/ElevenLabs | ⚠️ No conectado |
| Traducción por pivote | 🔲 Planificado |
| Post-procesamiento de texto | 🔲 Planificado |
| Modelo basado en proyectos | 🔲 Futuro |

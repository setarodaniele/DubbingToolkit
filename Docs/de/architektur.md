# Architektur und technische Referenz

Dieses Dokument beschreibt die interne Struktur des Projekts, die Hauptmodule, die Entwicklungskonventionen und den Status der Komponenten.

## Ordnerstruktur

```
DubbingToolkit/
├── Audio_Extracted/        Ausgabe der Audioextraktion
├── Audio_Input/            Direktes Audio-Eingabeverzeichnis
├── Billing/                TTS-Verbrauchsüberwachung
├── core/                   Gemeinsam genutzte Python-Module
├── credentials/            API-Anmeldedaten (von Git ausgeschlossen)
├── Dubbed/                 Endgültige TTS-Ausgabe
├── Installation/           Lokale Python-Laufzeitumgebungen
├── installer/              Build und Packaging
├── locale/                 Lokalisierung
│   ├── Active/             Aktive Sprach-JSON-Dateien
│   └── System/             Sprachmetadaten
├── Logs/                   Betriebsprotokolle
├── ps/                     PowerShell-Module
├── Repository/             Gemeinsam genutzte Ressourcen
├── Scripts/                Python-Skripte
│   └── maintenance/        Wartungsskripte
├── Settings/               Konfiguration
├── Subtitles/              Untertitel (Stub)
├── Temp/                   Temporäre Dateien
├── Tools/                  ffmpeg
├── Transcripts/            Transkriptions-SRT-Dateien
├── Translated/             Übersetzungs-SRT-Dateien
├── venv/                   Virtuelle Umgebung
├── Video_Input/            Quellvideos
└── voices/                 TTS-Stimmen
```

## Startkette

```
StartDubbing.bat
  └→ Scripts/Launcher.ps1
       └→ Scripts/Regista.py
```

## Pipeline

| Phase | Modul | Eingabe → Ausgabe |
|---|---|---|
| 1 — Audioextraktion | `Scripts/estrai_tracce.py` | `Video_Input/` → `Audio_Extracted/<ts>/` |
| 2 — Transkription | `Scripts/trascrivi_audio.py` | `Audio_Extracted/` → `Transcripts/<ts>/` |
| 3 — Übersetzung | `Scripts/traduci_testo.py` | `Transcripts/` → `Translated/<ts>/` |
| 4 — TTS | `Scripts/tts_menu.py` | `Translated/` → `Dubbed/` |

## Core-Module

### `messages.py`
```python
from core.messages import Messages
msg = Messages()
print(msg._("chiave_messaggio"))
```

### `credentials_manager.py`
Einzige autorisierte Stelle zum Lesen von `credentials/`.

### `api_check.py`
Überprüft Anmeldedaten vor dem TTS-Menü.

### `ui_printer.py` + `ui_colors.py`
Formatierte Konsolenausgabe.

### `utils_tts.py`
Gemeinsames SRT-Parsing.

### `file_selector.py`
Interaktive Dateiauswahl.

### `input_parsing.py`
Verarbeitung von Benutzereingaben.

## Scripts-Module

- `Regista.py` — Orchestrator
- `estrai_tracce.py` — Audioextraktion
- `trascrivi_audio.py` — Transkription
- `traduci_testo.py` — Übersetzung
- `tts_menu.py` / `tts_dubbing.py` — TTS-Pipeline
- `tts_azure.py` / `tts_google.py` — TTS-Backends
- `tts_merge.py` — Segmentzusammenführung
- `tts_config_manager.py` — TTS-Konfiguration
- `info_manager.py` — project_info.json
- `settings_manager.py` — settings.json
- `monitoraggio_consumo.py` — TTS-Verbrauch
- `menu_lingue.py` / `menu_lingue_tts.py` — Sprachauswahl
- `menu_voices.py` — Stimmenauswahl
- `backup_utils.py` — Sicherung

## Lokalisierung

```
locale/
├── Active/   it.json, en.json, es.json, de.json, fr.json, pt.json, ru.json, zh.json
└── System/   languages.json, whisper_languages.json
```

Regeln: Alle Meldungen über `core/messages.py`. Schlüssel in allen Dateien synchron halten.

### Wartungsskripte in `Scripts/maintenance/translation/`

| Skript | Funktion |
|---|---|
| `LocaleKeyAnalyzer.ps1` | Analyse fehlender Schlüssel |
| `LocaleTranslator.ps1` | Automatische Übersetzung |
| `Validate-LocaleJson.ps1` | JSON-Validierung |
| `Fix-LocaleDuplicates.ps1` | Duplikate beheben |
| `Clean-LocaleUnusedKeys.ps1` | Nicht verwendete Schlüssel entfernen |
| `Extract-Placeholders.ps1` | Platzhalter zuordnen |
| `Protect-Placeholders.ps1` | Platzhalter schützen |

## Konfiguration

```json
{
  "interface_lang": "it",
  "model": "small",
  "Transcript_Audio_Spoken_Lang": "it",
  "Translation_Target_Lang": "en",
  "Dubbing_Lang": "en"
}
```

| Feld | Beschreibung |
|---|---|
| `interface_lang` | Oberflächensprache |
| `model` | Whisper-Modell |
| `Transcript_Audio_Spoken_Lang` | Sprache des Quell-Audios |
| `Translation_Target_Lang` | Zielsprache der Übersetzung |
| `Dubbing_Lang` | TTS-Sprache |

## TTS-Stimmen

| Datei | Inhalt |
|---|---|
| `voices_azure.json` | Gefilterte Azure-Stimmen |
| `voices_azure_complete.json` | Vollständiger Azure-Katalog |
| `voices_google.json` | Gefilterte Google-Stimmen |
| `voices_google_complete.json` | Vollständiger Google-Katalog |
| `voices_index.json` | Einheitlicher Index |

## Build-System

```powershell
.\build.ps1              # interaktives Menü
.\build.ps1 -Test        # leichter Build
.\build.ps1 -Production  # vollständiger Build
.\build.ps1 -DryRun      # Simulation
```

| Datei | Zweck |
|---|---|
| `build_include.json` | Was kopiert wird |
| `build_exclude.json` | Globale Ausschlussliste |
| `build_exclude_test.json` | TEST-Ausschlussliste |
| `build_protected.json` | Geschützte Pfade |
| `build_empty_dirs.json` | Leere Ordner |

## Konventionen

| Element | Konvention |
|---|---|
| Ordner | `kleinbuchstaben_unterstrich` |
| Python-Module | `kleinbuchstaben_unterstrich.py` |
| Klassen | `CamelCase` |
| Funktionen/Variablen | `kleinbuchstaben_unterstrich` |
| Tests | Präfix `test_` |

Skriptstruktur:
```
# 1. IMPORTS / DEPENDENCIES
# 2. CONFIGURATION
# 3. UTILITIES
# 4. CORE LOGIC
# 5. MAIN EXECUTION
```

## Komponentenstatus

| Komponente | Status |
|---|---|
| Audioextraktion | ✅ Betriebsbereit |
| Whisper-Transkription | ✅ Betriebsbereit |
| Helsinki-NLP-Übersetzung | ✅ Betriebsbereit |
| TTS Azure | ✅ Betriebsbereit |
| TTS Google | ✅ Betriebsbereit |
| Mehrsprachige Oberfläche | ✅ Betriebsbereit |
| Verbrauchsüberwachung | ✅ Betriebsbereit |
| Build/Packaging | ✅ Betriebsbereit |
| Untertitel | ⚠️ Stub |
| Erweiterte Segmentierung | ⚠️ Platzhalter |
| WhisperX | ⚠️ Nicht integriert |
| TTS OpenAI/ElevenLabs | ⚠️ Nicht verbunden |
| Pivot-Übersetzung | 🔲 Geplant |
| Text-Nachbearbeitung | 🔲 Geplant |
| Projektbasiertes Modell | 🔲 Zukünftig |

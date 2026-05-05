# Architettura e riferimento tecnico

Questo documento descrive la struttura interna del progetto, i moduli principali, le convenzioni di sviluppo e lo stato dei componenti. È destinato principalmente a chi contribuisce allo sviluppo o vuole comprendere il funzionamento interno del sistema.

---

## Struttura delle cartelle

```
DubbingToolkit/
├── Audio_Extracted/        Output estrazione audio (sottocartelle per file)
├── Audio_Input/            Audio di input diretto
├── Billing/                Monitoraggio consumo e costi TTS
├── core/                   Moduli di supporto Python condivisi
├── credentials/            Credenziali API (escluse da Git)
├── Dubbed/                 Output TTS finale (per provider)
├── Installation/           Runtime Python locali (3.10, 3.11)
├── installer/              Sistema di build e packaging
├── locale/                 Localizzazione e gestione lingue
│   ├── Active/             File JSON lingua attivi (it, en, es, de, fr, pt, ru, zh)
│   └── System/             Metadati lingue (Whisper, lingue supportate)
├── Logs/                   Log operativi
├── ps/                     Moduli PowerShell (logging, messaggistica)
├── Repository/             Risorse condivise e modelli locali
├── Scripts/                Script operativi e moduli Python
│   └── maintenance/        Script di manutenzione e pipeline localizzazione
├── Settings/               Configurazione attiva e di riferimento
├── Subtitles/              Sottotitoli (da implementare)
├── Temp/                   File temporanei
├── Tools/                  Binari esterni (ffmpeg)
├── Transcripts/            Trascrizioni SRT (sottocartelle per file)
├── Translated/             Traduzioni SRT (sottocartelle per file)
├── venv/                   Ambiente virtuale Python principale
├── Video_Input/            Video sorgente (mai modificati)
└── voices/                 Voci TTS disponibili e campioni audio
```

---

## Catena di avvio

```
StartDubbing.bat
  └→ Scripts/Launcher.ps1
       Attiva venv, setup UTF-8, log, caricamento lingua
         └→ Scripts/Regista.py
              Menu principale e orchestrazione pipeline
```

Il Launcher gestisce: selezione del runtime Python locale (`Installation/`), creazione/attivazione del venv, setup del sistema di log, caricamento della lingua dell'interfaccia.

`Regista.py` è il coordinatore centrale: presenta il menu all'utente e delega l'esecuzione ai moduli specifici per ciascuna fase.

---

## Pipeline operativa

| Fase | Modulo | Input → Output |
|---|---|---|
| 1 — Estrazione audio | `Scripts/estrai_tracce.py` | `Video_Input/` → `Audio_Extracted/<ts>/` |
| 2 — Trascrizione | `Scripts/trascrivi_audio.py` | `Audio_Extracted/` o `Audio_Input/` → `Transcripts/<ts>/` (SRT) |
| 3 — Traduzione | `Scripts/traduci_testo.py` | `Transcripts/` → `Translated/<ts>/` (SRT) |
| 4 — TTS | `Scripts/tts_menu.py` | `Translated/` → `Dubbed/` (MP3/WAV) |

`tts_menu.py` delega a `tts_azure.py` o `tts_google.py` in base al provider attivo.

---

## Moduli core (`core/`)

Questi moduli sono condivisi da tutta la pipeline. Non devono essere chiamati direttamente dall'utente.

### `messages.py`
Sistema centralizzato di messaggistica localizzata. Legge `Settings/settings.json` → campo `interface_lang` → carica `locale/Active/<lang>.json`.

Utilizzo negli script:
```python
from core.messages import Messages
msg = Messages()
print(msg._("chiave_messaggio"))
```

Le chiavi mancanti producono il fallback `[MISSING: chiave]` e non causano crash. Tutte le chiavi mancanti devono essere corrette prima del rilascio.

### `credentials_manager.py`
Caricamento e validazione centralizzata delle credenziali API. È l'unico punto del progetto autorizzato a leggere i file in `credentials/`. Nessun altro modulo deve accedere direttamente a quei file.

### `api_check.py`
Verifica la validità delle credenziali prima di consentire l'accesso al menu TTS. Viene invocato automaticamente all'ingresso nel menu TTS.

### `ui_printer.py` + `ui_colors.py`
Funzioni per output console con formattazione e colori. Tutti gli script devono usare questi moduli invece di `print()` diretto, per garantire coerenza visiva.

### `utils_tts.py`
Utilità condivise per il parsing SRT, usate da entrambi i backend TTS.

### `file_selector.py`
Interfaccia per la selezione file tramite menu interattivo.

### `input_parsing.py`
Parsing e validazione degli input utente.

---

## Moduli Scripts principali

### `Regista.py`
Orchestratore principale. Gestisce il menu top-level e coordina l'esecuzione delle fasi della pipeline. Punto di ingresso Python dell'applicazione.

### `estrai_tracce.py`
Estrazione tracce audio dai video tramite ffmpeg. Genera una sottocartella in `Audio_Extracted/` con i file audio e il file `_info.txt`.

### `trascrivi_audio.py`
Trascrizione audio tramite Whisper (o WhisperX, quando integrato). Output in formato SRT in `Transcripts/`.

### `traduci_testo.py`
Traduzione SRT tramite modelli Helsinki-NLP MarianMT in esecuzione locale. Output in `Translated/`.

### `tts_dubbing.py` / `tts_menu.py`
Coordinamento della pipeline TTS. `tts_menu.py` è l'interfaccia utente; `tts_dubbing.py` gestisce il flusso di generazione e unione segmenti.

### `tts_azure.py` / `tts_google.py`
Backend TTS specifici per provider. Generano i segmenti audio e li salvano in `Dubbed/<PROVIDER>/`.

### `tts_merge.py`
Unione e sincronizzazione dei segmenti audio TTS nel file finale.

### `tts_config_manager.py`
Gestione configurazioni TTS: provider attivo, voce selezionata, parametri di sintesi.

### `info_manager.py`
Lettura e scrittura del file `project_info.json` nelle sottocartelle timestampate. Garantisce la tracciabilità dello stato tra le fasi.

### `settings_manager.py`
Lettura, validazione e accesso alle configurazioni in `Settings/settings.json`.

### `monitoraggio_consumo.py`
Accesso thread-safe al registro consumi TTS in `Billing/consumo_tts.json`.

### `menu_lingue.py` / `menu_lingue_tts.py`
Selezione lingue per trascrizione/traduzione e per pipeline TTS.

### `menu_voices.py`
Selezione e configurazione voci TTS dall'interfaccia.

### `backup_utils.py`
Gestione backup e storico file generati.

---

## Sistema di localizzazione

### Struttura

```
locale/
├── Active/              File lingua attivi (runtime)
│   ├── it.json
│   ├── en.json
│   ├── es.json
│   ├── de.json
│   ├── fr.json
│   ├── pt.json
│   ├── ru.json
│   └── zh.json
└── System/
    ├── languages.json           Lingue concettualmente supportate
    └── whisper_languages.json   Lingue supportate da Whisper
```

### Regole

- Tutti i messaggi dell'interfaccia Python devono usare `core/messages.py`.
- Tutti i file in `locale/Active/` devono essere sincronizzati: una chiave presente in `it.json` deve esistere in tutti gli altri file lingua.
- Le chiavi mancanti producono `[MISSING: key]` a runtime — non sono ammesse in ambiente stabile.
- PowerShell usa `ps/Messages.psm1` (sistema equivalente, separato).

### Pipeline di manutenzione localizzazione

In `Scripts/maintenance/translation/` è disponibile una pipeline completa per gestire i file lingua:

| Script | Funzione |
|---|---|
| `LocaleKeyAnalyzer.ps1` | Analisi chiavi mancanti e incoerenze tra file |
| `LocaleTranslator.ps1` | Traduzione automatica con protezione placeholder |
| `Validate-LocaleJson.ps1` | Validazione struttura e integrità JSON |
| `Fix-LocaleDuplicates.ps1` | Correzione chiavi duplicate |
| `Clean-LocaleUnusedKeys.ps1` | Rimozione chiavi non utilizzate |
| `Extract-Placeholders.ps1` | Estrazione e mappatura placeholder |

---

## Configurazione (`Settings/settings.json`)

Campi principali:

```json
{
  "interface_lang": "it",
  "model": "small",
  "Transcript_Audio_Spoken_Lang": "it",
  "Translation_Target_Lang": "en",
  "Dubbing_Lang": "en"
}
```

| Campo | Descrizione |
|---|---|
| `interface_lang` | Lingua dell'interfaccia utente |
| `model` | Modello Whisper da usare (`tiny`, `base`, `small`, `medium`, `large`) |
| `Transcript_Audio_Spoken_Lang` | Lingua parlata nell'audio sorgente |
| `Translation_Target_Lang` | Lingua di destinazione per la traduzione |
| `Dubbing_Lang` | Lingua per la sintesi TTS |

---

## Gestione voci TTS

Le voci disponibili sono catalogate in `voices/`:

| File | Contenuto |
|---|---|
| `voices_azure.json` | Voci Azure filtrate e pronte all'uso |
| `voices_azure_complete.json` | Catalogo completo Azure |
| `voices_google.json` | Voci Google filtrate |
| `voices_google_complete.json` | Catalogo completo Google |
| `voices_index.json` | Indice unificato tutte le voci (Azure + Google) con metadati |

I campioni audio delle voci (per ascolto) sono in `voices/voices_output/<provider>/<LANG-CODE>/<voice>.mp3`, se generati tramite `Scripts/VoicesRepository.py`.

Per aggiornare il catalogo voci dai provider:
```bash
voices/fetch_azure_voices.py
voices/fetch_google_voices.py
```

---

## Sistema di build e distribuzione

Il progetto include un sistema di packaging in `installer/`:

```powershell
installer/build.ps1
```

Le regole di inclusione/esclusione sono in:
- `installer/build_include.json`
- `installer/build_exclude.json`
- `installer/build_empty_dirs.json` — cartelle vuote da creare nel pacchetto

L'output va in `installer/build_payload/`. I file di credenziali reali non vengono mai inclusi nel build — solo i file `*.template.json`.

---

## Convenzioni di sviluppo

### Naming

| Elemento | Convenzione |
|---|---|
| Cartelle (nuove) | `minuscolo_underscore` |
| Moduli Python | `minuscolo_underscore.py` |
| Classi | `CamelCase` |
| Funzioni e variabili | `minuscolo_underscore` |
| Script di test | prefisso `test_` obbligatorio |

### Struttura degli script

Tutti gli script devono seguire la struttura numerata definita nella Sezione 6 di `RecapDubbing.txt`:

```
# 1. IMPORTS / DEPENDENCIES
# 2. CONFIGURATION – Paths, settings, constants
# 3. UTILITIES – Helper functions
# 4. CORE LOGIC – Main processing
# 5. MAIN EXECUTION – Entry point
```

Ogni script deve includere un'intestazione standard con nome, descrizione, input, output e note operative. I commenti nel codice devono essere in inglese.

### Messaggistica

- Nessuna stringa hardcoded nei moduli runtime.
- Tutti i messaggi provengono dai file JSON di localizzazione tramite `core/messages.py` (Python) o `ps/Messages.psm1` (PowerShell).
- Eccezione: script di bootstrap e script di manutenzione possono usare output non localizzato.

### Percorsi

Tutti i percorsi devono essere relativi alla root del progetto. Nessun percorso assoluto nei moduli runtime.

### File generati

Ogni fase della pipeline che genera file crea una sottocartella con formato:
```
<timestamp>_<nome_file_di_partenza>
```
e include un file `_info.txt` con metadati dell'elaborazione.

---

## Stato dei componenti

| Componente | Stato |
|---|---|
| Estrazione audio | ✅ Operativo |
| Trascrizione Whisper | ✅ Operativo |
| Traduzione Helsinki-NLP | ✅ Operativo |
| TTS Azure | ✅ Operativo |
| TTS Google | ✅ Operativo |
| Interfaccia multilingua (8 lingue) | ✅ Operativo |
| Monitoraggio consumo TTS | ✅ Operativo |
| Sistema di build/packaging | ✅ Operativo |
| Sottotitoli (menu opzione 5) | ⚠️ Stub — non implementato |
| Segmentazione avanzata | ⚠️ Placeholder — non in pipeline |
| WhisperX | ⚠️ Venv preparato, non integrato |
| TTS OpenAI / ElevenLabs | ⚠️ Credenziali presenti, non collegati al menu |
| Traduzione pivot (lingua intermedia) | 🔲 Pianificato |
| Post-processing testo (Traduzione→TTS) | 🔲 Pianificato |
| Modello project-based (cartella unica per progetto) | 🔲 Refactoring futuro |
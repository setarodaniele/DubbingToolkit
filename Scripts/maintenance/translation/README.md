# Translation Toolkit — Maintenance Scripts

Cartella: `Scripts\maintenance\translation\`

Questa cartella contiene gli strumenti di manutenzione e preparazione
per i file JSON di localizzazione del progetto DubbingToolkit.
Gli script lavorano in sequenza sul file sorgente definito in `config.json`
e producono report e backup organizzati per nome file sorgente.

---

## Struttura cartella

```
translation\
    ├── config.json                  ← configurazione centrale
    ├── README.md                    ← questo file
    │
    ├── Fix-LocaleDuplicates.ps1
    ├── Validate-LocaleJson.ps1
    ├── LocaleKeyAnalyzer.ps1
    ├── Clean-LocaleUnusedKeys.ps1
    ├── Extract-Placeholders.ps1
    ├── LocaleTranslator.ps1
    ├── Protect-Placeholders.ps1
    │
    ├── output\
    │     └── <lang>.json            ← file tradotti (es. en.json)
    │
    ├── Report\
    │     └── <nome_file_sorgente>\  ← sottocartella per file sorgente
    │           ├── key_report.txt
    │           ├── unused_key_clusters.txt
    │           ├── validate_locale_report.txt
    │           ├── placeholder_map.json
    │           └── placeholder_map.txt
    │
    └── backup\
          └── <nome_file_sorgente>\  ← sottocartella per file sorgente
                ├── <nome>_pre_dedup_N_YYYYMMDD.json
                ├── <nome>_duplicates_removed_N_YYYYMMDD.json
                ├── <nome>_pre_clean_N_YYYYMMDD.json
                └── <nome>_unused_removed_N_YYYYMMDD.json
```

---

## Configurazione — config.json

Tutti gli script leggono i percorsi da `config.json`.
Per cambiare file di lavoro è sufficiente modificare `source_file`.

| Chiave | Descrizione |
|---|---|
| `source_file` | File JSON sorgente da processare |
| `source_language` | Lingua sorgente (es. `it`) |
| `target_languages` | Lingue di destinazione (es. `["en"]`) |
| `report_folder` | Cartella base dei report |
| `backup_folder` | Cartella base dei backup |
| `scan_paths` | Cartelle del progetto da scansionare per l'analisi chiavi |
| `exclude_patterns` | Pattern di percorsi da escludere dalla scansione |
| `placeholder_map` | Path del file placeholder_map.json (usato dal translator) |
| `use_cache` | Abilita la cache delle traduzioni |
| `cache_dir` | Cartella della cache |
| `cache_file` | File della cache |

> **Nota:** report e backup vengono salvati in sottocartelle
> nominate come il file sorgente (senza estensione).
> Es: `source_file = Locale\Active\test.json` → sottocartella `test\`
> Questo permette di lavorare su file diversi senza sovrascrivere i dati.

> **Nota backup:** i file di backup usano una convenzione descrittiva con
> numero progressivo e data: `<nome>_pre_dedup_1_20260425.json`.
> Il numero progressivo evita sovrascritture se lo script viene eseguito
> più volte nella stessa giornata.

---

## Workflow — Fase 1: Pulizia e validazione

Da eseguire prima di ogni sessione di traduzione,
nell'ordine indicato.

### 1. Fix-LocaleDuplicates.ps1

Rileva e rimuove chiavi duplicate dal file JSON sorgente,
mantenendo sempre l'ultima occorrenza.

```powershell
# Solo analisi (nessuna modifica)
.\Fix-LocaleDuplicates.ps1

# Simulazione (mostra cosa verrebbe rimosso)
.\Fix-LocaleDuplicates.ps1 -DryRun

# Applica la pulizia
.\Fix-LocaleDuplicates.ps1 -Fix
```

**Output in modalità Fix:**
- `backup\<sorgente>\<nome>_pre_dedup_N_YYYYMMDD.json` — file originale completo
- `backup\<sorgente>\<nome>_duplicates_removed_N_YYYYMMDD.json` — chiavi duplicate eliminate

> **Nota:** `ConvertTo-Json` di PowerShell elimina automaticamente i duplicati
> anche in fase di traduzione, tenendo l'ultima occorrenza. Tuttavia eseguire
> questo script prima è importante per mantenere pulito il file sorgente e
> garantire risultati corretti di `LocaleKeyAnalyzer.ps1`.

---

### 2. Validate-LocaleJson.ps1

Controlla la qualità strutturale delle stringhe nel JSON.
Non modifica nulla — solo analisi e report.

```powershell
.\Validate-LocaleJson.ps1
```

**Controlli eseguiti:**

| Codice | Descrizione |
|---|---|
| `EMPTY_STRING` | Stringa vuota |
| `ONLY_SPACES` | Stringa composta solo da spazi |
| `LEADING_SPACE` | Spazio iniziale non voluto |
| `TRAILING_SPACE` | Spazio finale non voluto |
| `MULTIPLE_SPACES` | Spazi multipli interni |
| `PLACEHOLDER_UNBALANCED` | Parentesi graffe `{ }` non bilanciate |
| `EMPTY_PLACEHOLDER` | Placeholder vuoto `{}` — segnalato ma non bloccante |

**Output:**
- `Report\<sorgente>\validate_locale_report.txt`

---

### 3. LocaleKeyAnalyzer.ps1

Scansiona il codice sorgente del progetto e determina
quali chiavi del JSON sono effettivamente utilizzate.

```powershell
.\LocaleKeyAnalyzer.ps1
```

**Output:**
- `Report\<sorgente>\key_report.txt` — chiavi usate/inutilizzate + file mapping
- `Report\<sorgente>\unused_key_clusters.txt` — chiavi inutilizzate raggruppate per prefisso

> **Dipendenza:** richiede che `Fix-LocaleDuplicates` sia già stato eseguito.
> Rigenerare ogni volta che il codice sorgente o il JSON cambiano.

> **Nota:** la cartella `maintenance\translation\` è esclusa dalla scansione
> tramite `exclude_patterns` nel config per evitare falsi positivi causati
> dai nomi delle chiavi presenti nei commenti e nei log degli script stessi.

---

### 4. Clean-LocaleUnusedKeys.ps1

Rimuove dal JSON le chiavi identificate come inutilizzate
da `LocaleKeyAnalyzer.ps1`. Chiede conferma esplicita prima di applicare.

```powershell
.\Clean-LocaleUnusedKeys.ps1
```

**Output:**
- `backup\<sorgente>\<nome>_pre_clean_N_YYYYMMDD.json` — file originale completo
- `backup\<sorgente>\<nome>_unused_removed_N_YYYYMMDD.json` — chiavi eliminate

> **Dipendenza:** richiede `key_report.txt` generato da `LocaleKeyAnalyzer.ps1`.

> **Nota encoding:** il file viene scritto in UTF-8 senza BOM per preservare
> correttamente i caratteri accentati italiani (à, è, ì, ecc.).

---

## Workflow — Fase 2: Preparazione alla traduzione

### 5. Extract-Placeholders.ps1

Mappa tutti i placeholder presenti nel JSON pulito
e produce i file necessari alla pipeline di traduzione.

```powershell
.\Extract-Placeholders.ps1
```

**Placeholder rilevati:** `{0}`, `{}`, `{file_name}`, `{lang}`, `{confidence:.2f}` ecc.

**Output:**
- `Report\<sorgente>\placeholder_map.json` — mappa strutturata per la pipeline
- `Report\<sorgente>\placeholder_map.txt` — report leggibile per analisi manuale

> **Dipendenza:** va eseguito dopo la fase di pulizia (script 1-4).
> Rigenerare ogni volta che il JSON viene modificato.

> **Nota:** quando una chiave contiene un solo placeholder, PowerShell lo
> salva come stringa invece di array nel JSON. `Build-TokenMap` in
> `Protect-Placeholders.ps1` gestisce entrambi i casi correttamente.

---

## Workflow — Fase 3: Traduzione

### 6. Protect-Placeholders.ps1

Libreria di funzioni per la protezione dei placeholder durante la traduzione.
**Non va eseguita direttamente** — viene caricata via dot-sourcing da `LocaleTranslator.ps1`.

Funzioni esportate:

| Funzione | Descrizione |
|---|---|
| `Build-TokenMap` | Costruisce tokenMap e reverseMap dalla `placeholder_map.json` |
| `Invoke-MaskPlaceholders` | Sostituisce i placeholder con token `#NNN#` prima della traduzione |
| `Invoke-RestorePlaceholders` | Ripristina i placeholder originali dai token `#NNN#` dopo la traduzione |

---

### 7. LocaleTranslator.ps1

Traduce il file JSON sorgente nelle lingue configurate in `target_languages`
usando Google Cloud Translate API.

```powershell
.\LocaleTranslator.ps1
```

**Flusso per ogni chiave:**
1. Maschera i placeholder con `Invoke-MaskPlaceholders`
2. Invia il testo mascherato all'API di traduzione
3. Ripristina i placeholder con `Invoke-RestorePlaceholders`
4. Verifica l'integrità dei placeholder nel testo tradotto

**Cache su disco:**
Le traduzioni vengono salvate in cache (chiave SHA1 del testo mascherato + lingua).
Le chiamate API successive per testi già tradotti vengono evitate.
La cache viene salvata su disco solo se almeno una nuova traduzione è stata effettuata.

**Validazione pre-traduzione:**
Lo script valida il file sorgente prima di procedere e si interrompe in caso di:
`LEADING_SPACE`, `TRAILING_SPACE`, `MULTIPLE_SPACES`, `PLACEHOLDER_ATTACHED`

**Controlli post-traduzione:**
Per ogni chiave tradotta verifica che i placeholder siano intatti:
- `PLACEHOLDER_COUNT_MISMATCH` — numero di placeholder diverso dall'originale
- `PLACEHOLDER_ORDER_MISMATCH` — placeholder in ordine diverso dall'originale

**Dipendenze:**
- `Protect-Placeholders.ps1` — stessa cartella
- `placeholder_map.json` — generato da `Extract-Placeholders.ps1`
- `credentials\GoogleCloudTranslate.json` — relativo a projectRoot

**Output:**
- `output\<lang>.json` — file JSON tradotto per ogni lingua target (es. `output\en.json`)

> **Nota encoding:** `ConvertTo-Json` converte alcuni caratteri speciali in
> escape Unicode — `&` diventa `\u0026`, `->` diventa `\u003e`. È un
> comportamento normale di PowerShell, non causa problemi funzionali poiché
> qualsiasi parser JSON li interpreta correttamente.

---

## Sequenza completa

```
Fix-LocaleDuplicates  →  Validate-LocaleJson  →  LocaleKeyAnalyzer
       →  Clean-LocaleUnusedKeys  →  Extract-Placeholders
              →  Protect-Placeholders  →  LocaleTranslator
```

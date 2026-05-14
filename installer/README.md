# Sistema di Build e Installer — Dubbing Toolkit

Documentazione completa del sistema di build e packaging per l'installer di Dubbing Toolkit.

---

## 1. Panoramica del sistema

Il sistema produce un installer Windows eseguibile (`.exe`) per Dubbing Toolkit tramite una catena di tre strumenti:

```
build.ps1  →  build_manifest.ps1  →  Inno Setup (compilazione manuale)
```

**`build.ps1`** raccoglie i file del progetto applicando regole di inclusione/esclusione e li copia nella cartella `build_payload\`, che rappresenta il payload grezzo dell'installer.

**`build_manifest.ps1`** è uno strumento interattivo che classifica ogni elemento di `build_payload\` e genera i file di configurazione che Inno Setup utilizza per costruire l'installer. Aggiorna anche la procedura di pulizia nel file `.iss` principale.

**Inno Setup** legge `DubbingToolkit_setup.iss` (che include i file generati automaticamente) e compila l'installer finale in `InnoSetup\output\`.

---

## 2. Struttura delle cartelle

```
installer\
│
├── build.ps1                    Script di build del payload
├── build_manifest.ps1           Classificatore interattivo del manifest
│
├── build_include.json           Regole di inclusione file/cartelle
├── build_exclude.json           Regola di esclusione globale
├── build_exclude_test.json      Esclusioni aggiuntive solo in modalità TEST
├── build_empty_dirs.json        Cartelle vuote da creare nel payload
├── build_protected.json         Percorsi che bypassano le esclusioni
│
├── build_payload\               Output di build.ps1 — payload grezzo
│   └── (contenuto generato automaticamente, non modificare)
│
├── InnoSetup\
│   ├── DubbingToolkit_setup.iss        Script principale Inno Setup
│   ├── payload_sections.iss            Sezioni [Files][Dirs][UninstallDelete] (generato)
│   ├── payload_manifest.json           Manifest di classificazione (generato)
│   ├── assets\
│   │   ├── DubbingToolkit_Studio.ico
│   │   └── DubbingToolkit_Workspace.ico
│   └── output\                         Installer compilato (generato da Inno Setup)
│
└── Test\                         Script di test ad hoc
```

---

## 3. I file JSON di configurazione

### `build_include.json`

Definisce **cosa viene copiato** in `build_payload\`. Ogni entry ha tre campi:

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `source` | stringa | Percorso relativo alla radice del progetto |
| `dest` | stringa | Percorso di destinazione dentro `build_payload\` |
| `type` | stringa | Modalità di copia (vedi sotto) |

**Valori di `type`:**

- **`file`** — copia il singolo file indicato in `source`.
- **`full`** — copia la cartella intera con tutto il contenuto (rispettando le regole di esclusione, tranne per i percorsi protetti).
- **`sanitized`** — copia solo i file che corrispondono ai pattern elencati nel campo opzionale `include` (array di wildcard). Usato per `credentials\` dove si vogliono solo i file template e non le credenziali reali.

**Esempio di entry `sanitized`:**
```json
{
  "source": "credentials",
  "dest": "credentials",
  "type": "sanitized",
  "include": ["*template*.json", "README.md"]
}
```

---

### `build_exclude.json`

Lista di regole di esclusione **globali**, applicate in tutte le modalità di build. Ogni regola è una stringa: se il percorso assoluto di un file la contiene (match parziale), il file viene saltato.

Regole correnti: `nppBackup`, `\backup\`, `\installer\`, `\Temp\`, `\Temp2\`, `\Repository\`, `Installation\Python310`, `Scripts\Path`, `*.log`, `__pycache__`, `*.pyc`, script di manutenzione in `Scripts\maintenance\`.

---

### `build_exclude_test.json`

Regole di esclusione **aggiuntive** applicate solo in modalità **TEST**. Permettono build rapide saltando componenti pesanti:

- `Installation\Python310`, `Installation\Python311` — runtime Python (centinaia di MB)
- `Tools\ffmpeg` — binari ffmpeg
- `\voices` — modelli vocali

In modalità PRODUCTION queste regole non vengono caricate.

---

### `build_empty_dirs.json`

Elenco di cartelle che vengono **create vuote** in `build_payload\` indipendentemente da qualsiasi regola di inclusione. Rappresentano le directory di lavoro runtime che l'utente utilizza durante l'uso dell'applicazione:

`Audio_Input`, `Audio_Extracted`, `Dubbed`, `Transcripts`, `Translated`, `Video_Input`, `Output`, `Logs`, `Workspace`

---

### `build_protected.json`

Elenco di percorsi che vengono copiati **verbatim**, bypassando completamente le regole di esclusione globali. Usato per distribuzioni di terze parti (es. runtime Python) che non devono essere filtrate.

Percorso corrente protetto: `Installation\Python311`

---

## 4. `build.ps1`

### Modalità disponibili

| Modalità | Parametro | Comportamento |
|----------|-----------|---------------|
| **DRY-RUN** | `-DryRun` | Simula il packaging senza scrivere file. Stampa conteggio file e dimensione totale, poi esce. |
| **TEST** | `-Test` (default) | Build leggera: esclude Python runtime, ffmpeg e voices. Nessuna conferma richiesta. |
| **PRODUCTION** | `-Production` | Build completa con tutte le dipendenze. Richiede conferma esplicita (`Y`) prima di procedere. |

Se non viene passato alcun parametro, viene mostrato un **menu interattivo** che chiede di scegliere la modalità (1/2/3).

### Utilizzo

```powershell
# Menu interattivo
.\build.ps1

# Modalità esplicite
.\build.ps1 -DryRun
.\build.ps1 -Test
.\build.ps1 -Production
```

### Pipeline interna

```
[00] Selezione modalità
[01] Caricamento configurazione JSON
[02] Stampa riepilogo regole
[02.5] Simulazione file (solo DRY-RUN → esce qui)
[03] Conferma utente (solo PRODUCTION)
[04] Reset build_payload\ (cancellazione completa e ricreazione)
[05] Creazione cartelle vuote runtime
[06] Copia file secondo le regole include/exclude/protected/sanitized
[07] Riepilogo finale (file copiati, dimensione totale)
```

### Output atteso

Al termine di una build riuscita:
```
=== BUILD COMPLETE ===
Total files  : N
Total size   : X.X MB
```

Seguono istruzioni per eseguire il passo successivo (`build_manifest.ps1`).

> **Nota sicurezza:** `build_payload\` viene sempre **ricreata da zero** ad ogni build. Non inserire mai file manualmente al suo interno.

---

## 5. `build_manifest.ps1`

### Cos'è e quando va eseguito

`build_manifest.ps1` è uno strumento interattivo che va eseguito **dopo ogni esecuzione di `build.ps1`**. Legge il contenuto di `build_payload\` e mantiene un manifest JSON che classifica ogni elemento in base al suo comportamento durante installazione, aggiornamento e disinstallazione.

Al termine genera automaticamente:
- `InnoSetup\payload_manifest.json` — il manifest aggiornato
- `InnoSetup\payload_sections.iss` — le sezioni `[Files]`, `[Dirs]`, `[UninstallDelete]` per Inno Setup
- Aggiorna la procedura `FillAppFolders` in `DubbingToolkit_setup.iss` (tra i marcatori `##CLEANUP_BEGIN##` / `##CLEANUP_END##`)

### Opzioni C e R

All'avvio, se esiste già un manifest, viene chiesto cosa fare:

| Scelta | Quando usarla |
|--------|---------------|
| **C — Carica** | Nella maggior parte dei casi. Carica il manifest esistente come base e chiede di classificare solo gli elementi nuovi. |
| **R — Reset** | Solo se si vuole ripartire da zero con le classificazioni di default. Sovrascrive il manifest corrente. |

### Rilevamento elementi orfani

Prima di procedere con la classificazione, lo script confronta il manifest caricato con il contenuto fisico di `build_payload\`. Se trova **elementi nel manifest che non esistono fisicamente**, li mostra e chiede:

```
[!] Elementi nel manifest non trovati in build_payload (N):
    - nomecartella
    - nomefile
Vuoi rimuoverli automaticamente dal manifest? [s/N]:
```

- **S** — rimuove gli orfani dal manifest e continua
- **N** — avvisa che la compilazione Inno Setup potrebbe fallire, ma continua comunque

### Menu di classificazione S/U/G/M

Per ogni elemento nuovo trovato in `build_payload\` viene mostrato un menu:

| Opzione | Tipo | Comportamento |
|---------|------|---------------|
| **S — System** | `system` | File/cartella installata e sovrascritta ad ogni aggiornamento. Rimossa alla disinstallazione senza prompt. |
| **U — User** | `user` | Cartella creata vuota all'installazione. I dati utente vengono preservati durante gli aggiornamenti. Può essere soggetta a prompt di disinstallazione. |
| **G — Gruppo** | `user` | Applica automaticamente tutti i parametri di un gruppo predefinito (vedi legenda gruppi). |
| **M — Manuale** | qualsiasi | Inserimento campo per campo di tutti i valori. Per casi speciali non coperti dalle opzioni precedenti. |

### Domanda sul contenuto uniforme delle cartelle

Dopo aver classificato una **cartella** con S o U, viene chiesto:

```
Il contenuto della cartella è tutto dello stesso tipo? [S/n]:
```

- **S (sì, uniforme)** — la cartella viene classificata con `recursive: true`, gestita come unità intera.
- **N (no, misto)** — la cartella contenitore viene aggiunta con `recursive: false`, poi lo script scende dentro la cartella e classifica ogni elemento figlio separatamente. Per le sottocartelle la stessa domanda si ripete ricorsivamente.

### Legenda gruppi (opzione G)

| Gruppo | Tipo | Comportamento upgrade | Comportamento disinstallazione |
|--------|------|-----------------------|-------------------------------|
| **work_files** | user | Non toccata — dati utente preservati | Gestita dal checkbox "File di lavoro" (Audio, Trascrizioni, Traduzioni, ecc.) |
| **billing** | user | Non toccata — dati di fatturazione preservati | Gestita dal checkbox "Dati di fatturazione" |
| **credentials** | user | Non toccata — credenziali utente preservate | Gestita dal checkbox "Credenziali e chiavi API" — eliminazione condizionale solo se presenti file utente |

---

## 6. I file generati in InnoSetup

### `payload_manifest.json`

Il manifest è il registro centrale di classificazione. Contiene un array di entry, ognuna con questi flag:

| Flag | Tipo | Significato |
|------|------|-------------|
| `path` | stringa | Percorso relativo alla directory di installazione |
| `type` | `system` / `user` | Categoria dell'elemento |
| `install` | bool | Se `true`: il file/cartella viene copiata durante l'installazione |
| `create_empty` | bool | Se `true`: la cartella viene creata vuota (per le directory di lavoro utente) |
| `recursive` | bool | Se `true`: l'elemento è gestito ricorsivamente (tutta la sottostruttura) |
| `clean_on_upgrade` | bool | Se `true`: la cartella viene svuotata prima di reinstallare i file durante un aggiornamento |
| `remove_on_uninstall` | bool | Se `true`: l'elemento viene rimosso alla disinstallazione senza prompt |
| `uninstall_prompt` | bool | Se `true`: viene mostrato un checkbox all'utente durante la disinstallazione |
| `uninstall_prompt_default` | bool | Stato predefinito del checkbox (selezionato o deselezionato) |
| `uninstall_prompt_group` | stringa / null | Raggruppamento del checkbox (`work_files`, `billing`, `credentials`) |
| `uninstall_conditional` | bool | Se `true`: la rimozione avviene solo se sono presenti file utente nella cartella |

> **Non modificare manualmente** questo file. Viene rigenerato completamente a ogni esecuzione di `build_manifest.ps1`.

---

### `payload_sections.iss`

File Pascal generato automaticamente da `build_manifest.ps1`. Contiene le tre sezioni che Inno Setup usa per il packaging:

- **`[Files]`** — tutti i file/cartelle da installare (entry con `install: true`)
- **`[Dirs]`** — cartelle da creare vuote (entry con `create_empty: true`)
- **`[UninstallDelete]`** — elementi da rimuovere alla disinstallazione (entry con `remove_on_uninstall: true`)

È incluso in `DubbingToolkit_setup.iss` tramite:
```pascal
#include "payload_sections.iss"
```

> **Non modificare manualmente.** Viene rigenerato a ogni esecuzione di `build_manifest.ps1`.

---

### `DubbingToolkit_setup.iss`

Script principale di Inno Setup. Contiene tutta la logica dell'installer: UI, messaggi localizzati, codice Pascal per la gestione dell'installazione e della disinstallazione.

**Struttura delle sezioni principali:**

| Sezione | Contenuto |
|---------|-----------|
| `[Setup]` | Metadati: nome app, versione, percorso default, icone |
| `[Languages]` | Lingue supportate (7 lingue) |
| `[CustomMessages]` | Testi localizzati per UI e messaggi |
| `#include "payload_sections.iss"` | Sezioni Files/Dirs/UninstallDelete (generato) |
| `[Icons]` | Collegamento nel menu Start |
| `[Run]` | Azioni post-installazione |
| `[Code]` | Logica Pascal: form di disinstallazione, pulizia cartelle, validazione percorso |

**Marcatori `##CLEANUP_BEGIN##` / `##CLEANUP_END##`:**

All'interno della procedura `FillAppFolders` si trovano due commenti speciali:

```pascal
procedure FillAppFolders(AppFolders: TStringList);
begin
// ##CLEANUP_BEGIN##
  AppFolders.Add('core');
  AppFolders.Add('locale');
  // ...
// ##CLEANUP_END##
end;
```

Il contenuto tra questi marcatori viene **sostituito automaticamente** da `build_manifest.ps1` ogni volta che viene eseguito. Elenca le cartelle di sistema con `clean_on_upgrade: true` che devono essere svuotate durante un aggiornamento.

> **Non modificare il codice tra i marcatori.** Qualsiasi modifica manuale viene sovrascritta alla prossima esecuzione di `build_manifest.ps1`.
>
> **Non modificare `payload_sections.iss`** direttamente — viene incluso tramite `#include` ed è rigenerato automaticamente.

---

## 7. Workflow completo step by step

### Prima installazione da zero

1. Verificare che tutte le dipendenze siano presenti nella radice del progetto
2. Aprire PowerShell in `installer\`
3. Eseguire `.\build.ps1` e scegliere la modalità (TEST per iterazione rapida, PRODUCTION per release)
4. Eseguire `.\build_manifest.ps1` e scegliere **R** (reset) per generare il manifest da zero con i default
5. Classificare tutti gli elementi nuovi con S, U, G o M
6. Aprire Inno Setup Compiler e compilare `InnoSetup\DubbingToolkit_setup.iss`
7. L'installer si trova in `InnoSetup\output\`

---

### Aggiunta di nuovi file o cartelle al progetto

1. Aggiungere il percorso in `build_include.json` (se non già coperto da una regola `full` esistente)
2. Eseguire `.\build.ps1` (modalità TEST o PRODUCTION)
3. Eseguire `.\build_manifest.ps1` e scegliere **C** (carica)
4. Lo script rileva automaticamente gli elementi nuovi e chiede di classificarli
5. Classificare i nuovi elementi con S, U, G o M
6. Ricompilare con Inno Setup

---

### Rimozione di file o cartelle dal progetto

1. Rimuovere o aggiornare la regola in `build_include.json` (o aggiungere il percorso a `build_exclude.json`)
2. Eseguire `.\build.ps1` — l'elemento non sarà più in `build_payload\`
3. Eseguire `.\build_manifest.ps1` e scegliere **C** (carica)
4. Lo script rileva l'elemento come **orfano** (nel manifest ma non in `build_payload\`) e chiede se rimuoverlo
5. Rispondere **S** per rimuoverlo dal manifest
6. Ricompilare con Inno Setup

---

### Rilascio di una nuova versione

1. Aggiornare `AppVersion` in `DubbingToolkit_setup.iss` (sezione `[Setup]`)
2. Eseguire `.\build.ps1 -Production` e confermare con `Y`
3. Eseguire `.\build_manifest.ps1` e scegliere **C** (carica)
4. Rispondere alle eventuali domande su nuovi elementi o orfani
5. Aprire Inno Setup Compiler
6. Compilare `InnoSetup\DubbingToolkit_setup.iss`
7. L'installer finale si trova in `InnoSetup\output\setup_dubbing_toolkit.exe`

---

## 8. Avvertenze importanti

**Non modificare `build_payload\` manualmente.**
Viene cancellata e ricreata ad ogni build. Qualsiasi modifica manuale viene persa.

**Non modificare `payload_sections.iss` manualmente.**
È generato automaticamente da `build_manifest.ps1`. Modifiche manuali vengono sovrascritte alla prossima esecuzione.

**Non modificare il codice Pascal tra `##CLEANUP_BEGIN##` e `##CLEANUP_END##`.**
`build_manifest.ps1` sovrascrive quel blocco ad ogni esecuzione. Aggiornarlo significa aggiornare il manifest, non il `.iss` direttamente.

**Non includere mai credenziali reali nel build.**
Solo i file `*.template.json` vengono inclusi tramite la regola `sanitized` in `build_include.json`. I file `azure_speech_credentials.json` e `google_speech_credentials.json` reali sono in `.gitignore` e non devono mai essere copiati in `build_payload\`.

**Non saltare `build_manifest.ps1` dopo una build.**
Se `build_payload\` cambia ma il manifest non viene aggiornato, `payload_sections.iss` non corrisponde al payload reale e la compilazione Inno Setup genererà un installer incompleto o non compilabile.

**Non usare la modalità PRODUCTION per iterazione rapida.**
La modalità TEST esiste appositamente per questo: esclude Python, ffmpeg e voices, riducendo il tempo di build da minuti a secondi.

**Non rispondere N agli orfani se si intende compilare.**
Elementi orfani nel manifest (percorsi che non esistono in `build_payload\`) causano errori di compilazione in Inno Setup perché `payload_sections.iss` referenzierà file non presenti.

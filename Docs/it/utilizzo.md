# Guida all'utilizzo

Questa guida descrive il flusso operativo di DubbingToolkit, dalla preparazione dei file di input fino all'audio doppiato finale.

---

## Avvio del progetto

Fare doppio clic su `StartDubbing.bat`. Il progetto si avvia e presenta l'interfaccia principale con il menu di gestione dei progetti.

---

## Creazione e selezione di un progetto

Dalla schermata principale, selezionare "Gestione progetti" (opzione 0) e creare un nuovo progetto. Ogni progetto è uno spazio di lavoro isolato per un video specifico.

Una volta creato, il progetto viene impostato come attivo e rimane disponibile per le operazioni successive.

---

## Flusso operativo

Il processo si articola in 4 fasi. Ogni fase può essere eseguita singolarmente o come parte del flusso completo.

| Fase | Operazione            | Cartella output                              |
|------|-----------------------|----------------------------------------------|
| 1    | Estrazione audio      | `Workspace/projects/{nome}/audio_extraction/current/` |
| 2    | Trascrizione          | `Workspace/projects/{nome}/transcripts/current/`      |
| 3    | Traduzione            | `Workspace/projects/{nome}/translated/current/`       |
| 4    | Sintesi vocale (TTS)  | `Workspace/projects/{nome}/dubbed/current/`           |

> **Importante:** dopo la trascrizione e dopo la traduzione è consigliata una verifica manuale del testo generato. Le correzioni permettono di migliorare la qualità dell'audio finale e di gestire eventuali incongruenze con le tempistiche del parlato originale.

---

## Preparazione dell'input

### Input video

Durante l'estrazione audio, il sistema presenta un dialog di importazione che permette di:
1. Usare il video da una posizione esterna (mantiene il path originale)
2. Copiare il video nel progetto (`Workspace/projects/{nome}/video_input/`)
3. Spostare il video nel progetto

Formati supportati: quelli gestiti da ffmpeg (mp4, mkv, avi, mov, ecc.).

### Input audio diretto

Se si dispone già dell'audio estratto, durante la trascrizione è possibile selezionare manualmente un file audio dalla cartella `Workspace/projects/{nome}/audio_input/` oppure da una posizione esterna. In questo caso la Fase 1 — Estrazione audio può essere saltata.

---

## Fase 1 — Estrazione audio

Il sistema estrae le tracce audio dal video tramite ffmpeg. Tutti i file audio estratti vengono salvati in `Workspace/projects/{nome}/audio_extraction/current/` con nomi `track_01.wav`, `track_02.wav`, ecc.

Per ogni traccia viene generato automaticamente un file di metadati (`track_XX_metadata.json`) con informazioni sul codec, sample rate, durata e altre proprietà.

---

## Fase 2 — Trascrizione

L'audio viene trascritto in formato SRT. La lingua del parlato viene rilevata automaticamente e può essere modificata dal menu prima di avviare la trascrizione. Il risultato viene salvato in `Workspace/projects/{nome}/transcripts/current/`.

> **Consiglio:** prima di procedere alla traduzione, verificare e correggere il testo trascritto. Errori in questa fase si ripercuotono su tutte le fasi successive.

---

## Fase 3 — Traduzione

Il file SRT trascritto viene tradotto nella lingua di destinazione. La traduzione avviene completamente in locale. I modelli necessari vengono scaricati automaticamente alla prima esecuzione per ciascuna coppia di lingue. Il risultato viene salvato in `Workspace/projects/{nome}/translated/current/`.

Se la coppia di lingue diretta non è disponibile, è prevista in futuro una traduzione pivot tramite inglese come lingua intermedia.

> **Consiglio:** verificare il testo tradotto prima di avviare la sintesi. Le correzioni manuali permettono di gestire eventuali incongruenze con le tempistiche del parlato originale.

---

## Fase 4 — Sintesi vocale (TTS)

Il testo tradotto viene sintetizzato vocalmente, segmento per segmento, tramite il provider TTS selezionato. I segmenti vengono poi uniti nel file audio finale, salvato in `Workspace/projects/{nome}/dubbed/current/`.

### Provider TTS

Il sistema supporta attualmente due provider:

- **Azure Cognitive Services Speech** — servizio TTS cloud di Microsoft
- **Google Cloud Text-to-Speech** — servizio TTS cloud di Google

Provider e voce si selezionano direttamente dal menu TTS. Il sistema include una funzione dedicata per ascoltare i campioni audio delle voci disponibili prima di avviare la sintesi.

### Monitoraggio dei costi

All'avvio del modulo TTS viene presentato automaticamente un consumo stimato. Per verificare il consumo reale consultare direttamente il pannello del proprio provider.

---

## Lingua dell'interfaccia

La lingua dell'interfaccia si seleziona all'avvio e può essere modificata in qualsiasi momento dal menu impostazioni senza riavviare il progetto.

---

## Gestione dei progetti

### Duplicazione

È possibile duplicare un progetto esistente per creare una copia con un nuovo nome. Utile per testare variazioni della stessa sorgente.

### Rinomina

Un progetto può essere rinominato in qualsiasi momento dalla gestione progetti. Se il progetto è attivo, il puntatore attivo viene aggiornato automaticamente.

### Eliminazione

Un progetto può essere eliminato. Se abilitata l'impostazione `use_trash`, il progetto viene spostato nel Cestino; altrimenti viene eliminato definitivamente.

### Apertura cartella

È possibile aprire direttamente la cartella di un progetto in Explorer per ispezionare manualmente i file generati.

---

## Consigli operativi

- Usare nomi file e progetti brevi e senza spazi o caratteri speciali per evitare problemi nei percorsi.
- I file in `Workspace/projects/{nome}/video_input/` non vengono mai modificati dal sistema.
- Ogni fase genera metadati (file `.json` o `_info.txt`): utili per tracciare lo stato di avanzamento o diagnosticare problemi.
- In caso di interruzione del processo, è possibile ripartire dalla fase successiva a quella già completata, usando i file nelle cartelle di output intermedio.
- I file estratti e processati in ogni fase vengono automaticamente archiviati nella cartella `archive/` di quella fase per preservare la cronologia.

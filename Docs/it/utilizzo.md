# Guida all'utilizzo

Questa guida descrive il flusso operativo di DubbingToolkit, dalla preparazione dei file di input fino all'audio doppiato finale.

---

## Avvio del progetto

Fare doppio clic su `StartDubbing.bat`. Il progetto si avvia e presenta l'interfaccia principale. Al primo avvio verranno installate automaticamente tutte le dipendenze necessarie.

---

## Flusso operativo

Il processo si articola in 4 fasi. Ogni fase può essere eseguita singolarmente o come parte del flusso completo.

| Fase | Operazione            | Output              |
|------|-----------------------|---------------------|
| 1    | Estrazione audio      | `Audio_Extracted/`  |
| 2    | Trascrizione          | `Transcripts/`      |
| 3    | Traduzione            | `Translated/`       |
| 4    | Sintesi vocale (TTS)  | `Dubbed/`           |

> **Importante:** dopo la trascrizione e dopo la traduzione è consigliata una verifica manuale del testo generato. Le correzioni permettono di migliorare la qualità dell'audio finale e di gestire eventuali incongruenze con le tempistiche del parlato originale. In futuro sarà disponibile un sistema automatico di verifica della coerenza tra testo e tempistiche audio.

---

## Preparazione dell'input

### Input video

È possibile posizionare i file video nella cartella `Video_Input/` oppure selezionarli manualmente dall'interfaccia. In futuro sarà prevista esclusivamente la selezione manuale.

Formati supportati: quelli gestiti da ffmpeg (mp4, mkv, avi, mov, ecc.).

### Input audio diretto

Se si dispone già dell'audio estratto, è possibile posizionarlo nella cartella `Audio_Input/` oppure selezionarlo manualmente. In questo caso la Fase 1 — Estrazione audio può essere saltata.

---

## Fase 1 — Estrazione audio

Il sistema estrae le tracce audio dal video tramite ffmpeg. Per ogni file processato viene creata automaticamente una sottocartella in `Audio_Extracted/` contenente i file audio estratti e un file `_info.txt` con i metadati dell'estrazione.

---

## Fase 2 — Trascrizione

L'audio viene trascritto in formato SRT. La lingua del parlato viene rilevata automaticamente e può essere modificata dal menu prima di avviare la trascrizione. Il risultato viene salvato in `Transcripts/`.

> **Consiglio:** prima di procedere alla traduzione, verificare e correggere il testo trascritto. Errori in questa fase si ripercuotono su tutte le fasi successive.

---

## Fase 3 — Traduzione

Il file SRT trascritto viene tradotto nella lingua di destinazione. La traduzione avviene completamente in locale. I modelli necessari vengono scaricati automaticamente alla prima esecuzione per ciascuna coppia di lingue. Il risultato viene salvato in `Translated/`.

Se la coppia di lingue diretta non è disponibile, è prevista in futuro una traduzione pivot tramite inglese come lingua intermedia.

> **Consiglio:** verificare il testo tradotto prima di avviare la sintesi. Le correzioni manuali permettono di gestire eventuali incongruenze con le tempistiche del parlato originale.

---

## Fase 4 — Sintesi vocale (TTS)

Il testo tradotto viene sintetizzato vocalmente, segmento per segmento, tramite il provider TTS selezionato. I segmenti vengono poi uniti nel file audio finale, salvato in `Dubbed/`.

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

## Consigli operativi

- Usare nomi file brevi e senza spazi o caratteri speciali per evitare problemi nei percorsi.
- I file in `Video_Input/` non vengono mai modificati dal sistema.
- Ogni fase genera un file `_info.txt` con i metadati: utile per tracciare lo stato di avanzamento o diagnosticare problemi.
- In caso di interruzione del processo, è possibile ripartire dalla fase successiva a quella già completata, usando i file nelle cartelle di output intermedio.
# FAQ e risoluzione problemi

---

## Avvio e ambiente

**Il progetto non si avvia con `StartDubbing.bat`.**

Una causa comune è il blocco all'esecuzione degli script PowerShell. 
Aprire PowerShell come amministratore ed eseguire:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
Poi riprovare l'avvio.

---

**Il venv risulta corrotto o non si attiva.**

Eliminare manualmente la cartella `venv/` all'interno della cartella del progetto. Al successivo avvio tramite `StartDubbing.bat`, il Launcher rileverà l'assenza del venv e lo ricreerà automaticamente.

---

**Errore `[MISSING: key]` nell'interfaccia.**

Indica che una chiave è assente nel file di localizzazione attivo. Non è bloccante ma riduce la chiarezza dell'interfaccia. Segnalare la chiave mancante per consentirne la correzione.

---

## Credenziali e API

**Il sistema segnala credenziali Azure non valide.**

Verificare che `credentials/azure_speech_credentials.json` contenga i campi `subscription` (chiave API) e `region` (es. `westeurope`). Usare `credentials/azure_speech_credentials.template.json` come riferimento per la struttura corretta.

---

**Il sistema segnala credenziali Google non valide.**

`credentials/google_speech_credentials.json` deve essere il file JSON completo di un service account GCP con il ruolo Cloud Text-to-Speech abilitato. Verificare che il file non sia troncato o malformato.

> Per la creazione delle credenziali Azure e Google sono disponibili guide dedicate nella stessa cartella di questa documentazione.

---

## Trascrizione

**La trascrizione produce risultati imprecisi o in lingua sbagliata.**

Specificare manualmente la lingua sorgente tramite il menu lingue prima di avviare la trascrizione. Le lingue disponibili sono elencate nel menu di selezione lingua.

---

**La trascrizione è molto lenta.**

La velocità dipende dal modello Whisper selezionato e dall'hardware disponibile. Il modello si seleziona direttamente nel menu di trascrizione prima di avviare il processo.

| Modello | Velocità | Qualità |
|---|---|---|
| `tiny` | Molto alta | Base |
| `base` | Alta | Discreta |
| `small` | Media | Buona |
| `medium` | Bassa | Alta |
| `large` | Molto bassa | Massima |

Su CPU senza GPU dedicata, anche il modello `small` può essere lento su file lunghi.

---

**La trascrizione si interrompe con errore di memoria.**

File audio molto lunghi caricati interamente in RAM possono causare problemi su sistemi con poca memoria. Considerare di suddividere il file audio in segmenti più brevi prima della trascrizione.

---

## Traduzione

**La coppia di lingue desiderata non è disponibile.**

Non tutte le coppie linguistiche hanno un modello Helsinki-NLP diretto disponibile. Le coppie supportate sono elencate nel menu di selezione lingua. La traduzione via lingua pivot (inglese come intermedio) è pianificata ma non ancora implementata.

---

**Il testo tradotto contiene errori o suona innaturale.**

I modelli Helsinki-NLP sono modelli di traduzione automatica e possono produrre imprecisioni, specialmente su frasi idiomatiche o termini tecnici. Il post-processing del testo è pianificato come miglioramento futuro.

---

## Sintesi TTS

**Il TTS genera audio con pause o ritmi innaturali.**

Verificare la voce selezionata nel menu TTS. Le voci neurali (Azure Neural, Google WaveNet) producono risultati significativamente migliori rispetto alle voci standard. È possibile ascoltare i campioni audio prima di avviare la sintesi.

---

**L'output TTS è silenzioso o contiene solo rumore.**

Aprire il file SRT tradotto in `Translated/` con un editor di testo e verificare che contenga segmenti validi con testo non vuoto.

---

**Il monitoraggio consumo non si aggiorna.**

Il consumo viene registrato in `Billing/consumo_tts.json`. Se il file risulta bloccato o corrotto, farne un backup, cancellarlo e verrà ricreato automaticamente al prossimo utilizzo.

---

## File e cartelle

**Non trovo l'output generato.**

Ogni fase crea una sottocartella con formato `<timestamp>_<nome_file>` nella propria directory di output. Cercare in:
- `Audio_Extracted/` per l'audio estratto
- `Transcripts/` per le trascrizioni SRT
- `Translated/` per le traduzioni SRT
- `Dubbed/<PROVIDER>/` per l'audio doppiato finale

Il file `_info.txt` in ogni sottocartella riporta i dettagli dell'elaborazione.

---

**Ho spostato il progetto e ora non funziona più.**

Eliminare manualmente la cartella `venv/`. Al successivo avvio tramite `StartDubbing.bat`, il Launcher ricreerà il venv nella nuova posizione.

---

## Build e distribuzione

**Le credenziali API non sono incluse nel pacchetto di distribuzione.**

È il comportamento corretto. Le credenziali Azure e Google non vengono mai incluse nel pacchetto per motivi di sicurezza. Vanno inserite manualmente nella cartella `credentials/` su ogni macchina dopo l'installazione, seguendo la struttura dei file template.

---

## Domande generali

**È possibile usare il progetto senza connessione internet?**

Parzialmente. La trascrizione (Whisper) e la traduzione (Helsinki-NLP) funzionano offline dopo che i modelli sono stati scaricati. La sintesi TTS (Azure, Google) richiede connessione internet in quanto usa API cloud.

---

**È possibile aggiungere nuove lingue all'interfaccia?**

Sì. Nuove lingue verranno aggiunte progressivamente nel tempo. Per richiedere una lingua specifica è possibile contattare direttamente il progetto. Chi volesse aggiungerla autonomamente deve:

1. Creare il file `locale/Active/<codice_lingua>.json` seguendo la struttura degli altri file lingua esistenti
2. Aggiungere la nuova lingua in `locale/System/languages.json`

Entrambi i passaggi sono necessari: senza il secondo la lingua non verrà riconosciuta dal sistema.

---

**Il progetto supporta l'elaborazione batch di più video?**

Al momento il flusso è progettato per un file alla volta. È possibile preparare più file e processarli in sequenza, ma non esiste una modalità batch automatica. Questa funzionalità è considerata per sviluppi futuri.
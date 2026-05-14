# DubbingToolkit

> ℹ️ **Nota**: La documentazione in altre lingue è tradotta automaticamente e potrebbe contenere errori o imprecisioni.

**DubbingToolkit** è un sistema di doppiaggio ibrido Python + PowerShell che consente di trascrivere, tradurre e risintetizzare vocalmente contenuti audio/video in più lingue, utilizzando motori TTS professionali (Azure, Google) e modelli di trascrizione locali (Whisper).

---

## Indice della documentazione

| File | Contenuto |
|---|---|
| [README.md](README.md) | Questa pagina — panoramica generale |
| [installazione.md](installazione.md) | Requisiti, setup e configurazione iniziale |
| [utilizzo.md](utilizzo.md) | Guida operativa e flusso di lavoro |
| [architettura.md](architettura.md) | Struttura del progetto, moduli e convenzioni |
| [faq.md](faq.md) | Domande frequenti e risoluzione problemi |
| [limitazioni_note.md](limitazioni_note.md) | Limitazioni attuali e funzionalità non ancora implementate |
| [credenziali_azure.md](credenziali_azure.md) | Configurazione credenziali Azure |
| [credenziali_google.md](credenziali_google.md) | Configurazione credenziali Google |

---

## Cosa fa

DubbingToolkit orchestra le fasi principali del doppiaggio — estrazione audio, trascrizione, traduzione e sintesi vocale — riducendo drasticamente il lavoro manuale e centralizzando l'intero processo in un'unica pipeline controllata.

1. **Estrazione audio** — Estrae le tracce audio dai file video tramite ffmpeg. Può essere saltata se si dispone già dell'audio.
2. **Trascrizione** — Trascrive l'audio in formato SRT tramite Whisper.
3. **Traduzione** — Traduce i sottotitoli SRT nella lingua di destinazione usando modelli Helsinki-NLP in esecuzione locale, senza dipendenze da API esterne.
4. **Sintesi vocale (TTS)** — Genera l'audio doppiato segmento per segmento tramite Azure TTS o Google TTS, poi unisce i segmenti nel file audio finale.

---

## Lingue supportate

L'interfaccia del sistema è disponibile attualmente in 8 lingue:

| Codice | Lingua |
|---|---|
| `it` | Italiano |
| `en` | Inglese |
| `es` | Spagnolo |
| `de` | Tedesco |
| `fr` | Francese |
| `pt` | Portoghese |
| `ru` | Russo |
| `zh` | Cinese |

Le lingue di trascrizione e traduzione dipendono rispettivamente da Whisper e dai modelli Helsinki-NLP disponibili. Vedi `locale/` per i dettagli.

---

## Provider TTS supportati attualmente

- **Azure Cognitive Services Speech** — alta qualità, voci neurali, ampia copertura linguistica
- **Google Cloud Text-to-Speech** — alternativa affidabile con buona varietà di voci

Entrambi i provider richiedono credenziali API configurate localmente. Vedi [installazione.md](installazione.md).

---

## Entry point

Il progetto si avvia da un unico file:

```
StartDubbing.bat
```

Tutto il resto è orchestrato automaticamente dal Launcher.

---

## Stato del progetto

DubbingToolkit è in sviluppo attivo. Alcune funzionalità sono già operative nella pipeline principale; altre sono pianificate come miglioramenti futuri (segmentazione avanzata, post-processing testo, traduzione pivot, ecc.). Vedi [architettura.md](architettura.md) per i dettagli sullo stato dei moduli.
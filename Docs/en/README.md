# DubbingToolkit

> ℹ️ **Note**: Documentation in other languages is automatically translated and may contain errors or inaccuracies.

**DubbingToolkit** is a hybrid Python + PowerShell dubbing system that allows you to transcribe, translate, and re-synthesize audio/video content in multiple languages, using professional TTS engines (Azure, Google) and local transcription models (Whisper).

---

## Documentation Index

| File | Contents |
|---|---|
| [README.md](README.md) | This page — general overview |
| [installation.md](installation.md) | Requirements, setup, and initial configuration |
| [usage.md](usage.md) | Operational guide and workflow |
| [architecture.md](architecture.md) | Project structure, modules, and conventions |
| [faq.md](faq.md) | Frequently asked questions and troubleshooting |
| [limitations_notes.md](limitations_notes.md) | Current limitations and not-yet-implemented features |
| [credenziali_azure.md](credenziali_azure.md) | Azure credentials configuration |
| [credenziali_google.md](credenziali_google.md) | Google credentials configuration |

---

## What It Does

DubbingToolkit orchestrates the main stages of dubbing — audio extraction, transcription, translation, and speech synthesis — drastically reducing manual work and centralizing the entire process in a single controlled pipeline.

1. **Audio extraction** — Extracts audio tracks from video files via ffmpeg. Can be skipped if you already have the audio.
2. **Transcription** — Transcribes audio into SRT format via Whisper.
3. **Translation** — Translates SRT subtitles into the target language using Helsinki-NLP models running locally, with no dependency on external APIs.
4. **Text-to-speech (TTS)** — Generates dubbed audio segment by segment via Azure TTS or Google TTS, then merges the segments into the final audio file.

---

## Supported Languages

The system interface is currently available in 8 languages:

| Code | Language |
|---|---|
| `it` | Italian |
| `en` | English |
| `es` | Spanish |
| `de` | German |
| `fr` | French |
| `pt` | Portuguese |
| `ru` | Russian |
| `zh` | Chinese |

Transcription and translation languages depend on Whisper and the available Helsinki-NLP models respectively. See `locale/` for details.

---

## Currently Supported TTS Providers

- **Azure Cognitive Services Speech** — high quality, neural voices, broad language coverage
- **Google Cloud Text-to-Speech** — reliable alternative with a good variety of voices

Both providers require API credentials configured locally. See [installation.md](installation.md).

---

## Entry Point

The project is launched from a single file:

```
StartDubbing.bat
```

Everything else is orchestrated automatically by the Launcher.

---

## Project Status

DubbingToolkit is under active development. Some features are already operational in the main pipeline; others are planned as future improvements (advanced segmentation, text post-processing, pivot translation, etc.). See [architecture.md](architecture.md) for details on module status.

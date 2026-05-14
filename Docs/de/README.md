# DubbingToolkit

> ⚠️ **Warnung**: Diese Dokumentation wurde automatisch übersetzt und kann Fehler oder Ungenauigkeiten enthalten. Für eine detaillierte Erklärung konsultieren Sie bitte die Version auf [Englisch](../en/README.md).

**DubbingToolkit** ist ein hybrides Python- und PowerShell-Synchronisationssystem, das es ermöglicht, Audio- und Videoinhalte in mehrere Sprachen zu transkribieren, zu übersetzen und per Sprachsynthese neu zu vertonen — unter Verwendung professioneller TTS-Engines (Azure, Google) und lokaler Transkriptionsmodelle (Whisper).

## Dokumentationsübersicht

| Datei | Inhalt |
|---|---|
| [README.md](README.md) | Diese Seite — Allgemeine Übersicht |
| [installation.md](installation.md) | Systemanforderungen, Einrichtung und Erstkonfiguration |
| [verwendung.md](verwendung.md) | Bedienungsanleitung und Arbeitsablauf |
| [architektur.md](architektur.md) | Projektstruktur, Module und Konventionen |
| [faq.md](faq.md) | Häufig gestellte Fragen und Fehlerbehebung |
| [einschränkungen_und_notizen.md](einschränkungen_und_notizen.md) | Aktuelle Einschränkungen |
| [credenziali_azure.md](credenziali_azure.md) | Azure-Anmeldedaten konfigurieren |
| [credenziali_google.md](credenziali_google.md) | Google-Anmeldedaten konfigurieren |

## Was das Tool tut

1. **Audioextraktion** — ffmpeg
2. **Transkription** — Whisper
3. **Übersetzung** — Helsinki-NLP lokal
4. **Sprachsynthese (TTS)** — Azure TTS oder Google TTS

## Unterstützte Sprachen

| Code | Sprache |
|---|---|
| `it` | Italienisch |
| `en` | Englisch |
| `es` | Spanisch |
| `de` | Deutsch |
| `fr` | Französisch |
| `pt` | Portugiesisch |
| `ru` | Russisch |
| `zh` | Chinesisch |

## TTS-Anbieter

- **Azure Cognitive Services Speech**
- **Google Cloud Text-to-Speech**

Siehe [installation.md](installation.md).

## Einstiegspunkt

```
StartDubbing.bat
```

## Projektstatus

In aktiver Entwicklung. Siehe [architektur.md](architektur.md).

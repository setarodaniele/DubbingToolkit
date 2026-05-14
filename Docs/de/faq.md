# FAQ und Fehlerbehebung

## Start und Umgebung

**Das Projekt startet nicht.**
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Die virtuelle Umgebung lässt sich nicht aktivieren.**
`venv/` löschen und `StartDubbing.bat` neu starten.

**Fehler `[MISSING: key]`.**
Schlüssel fehlt in der Lokalisierungsdatei. Nicht blockierend.

## Anmeldedaten und APIs

**Azure-Anmeldedaten ungültig.**
`subscription` und `region` in `credentials/azure_speech_credentials.json` überprüfen.

**Google-Anmeldedaten ungültig.**
Die JSON-Datei muss ein vollständiges GCP-Dienstkonto mit aktiviertem Cloud Text-to-Speech sein.

## Transkription

**Ungenaue Ergebnisse oder falsche Sprache.**
Sprache manuell über das Menü angeben.

**Transkription ist langsam.**

| Modell | Geschwindigkeit | Qualität |
|---|---|---|
| `tiny` | Sehr hoch | Grundlegend |
| `base` | Hoch | Ausreichend |
| `small` | Mittel | Gut |
| `medium` | Niedrig | Hoch |
| `large` | Sehr niedrig | Maximal |

**Speicherfehler.**
Audio in kürzere Segmente aufteilen.

## Übersetzung

**Sprachpaar nicht verfügbar.**
Nicht alle Helsinki-NLP-Paare sind verfügbar. Pivot-Übersetzung ist geplant.

**Übersetzter Text mit Fehlern.**
Helsinki-NLP kann Ungenauigkeiten aufweisen. Nachbearbeitung ist geplant.

## Sprachsynthese (TTS)

**Audio mit unnatürlichen Pausen.**
Neuronale Stimmen verwenden (Azure Neural, Google WaveNet).

**Stille Ausgabe.**
`Translated/` auf gültige Segmente prüfen.

**Verbrauchsüberwachung wird nicht aktualisiert.**
`Billing/consumo_tts.json` sichern und löschen.

## Dateien und Ordner

**Ausgabe nicht gefunden.**
- `Audio_Extracted/`
- `Transcripts/`
- `Translated/`
- `Dubbed/<PROVIDER>/`

**Projekt verschoben, funktioniert nicht mehr.**
`venv/` löschen.

## Build und Verteilung

**Anmeldedaten nicht im Paket.**
Korrektes Verhalten. Nach der Installation manuell einfügen.

## Allgemeine Fragen

**Offline-Nutzung?**
Teilweise möglich. TTS benötigt eine Internetverbindung.

**Sprachen hinzufügen?**
1. `locale/Active/<code>.json`
2. `locale/System/languages.json`

**Stapelverarbeitung?**
Nein, derzeit eine Datei pro Vorgang.

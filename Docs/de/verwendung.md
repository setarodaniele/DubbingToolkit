# Bedienungsanleitung

Diese Anleitung beschreibt den Operativen Arbeitsablauf von DubbingToolkit, von der Vorbereitung der Eingabedateien bis zur endgültigen synchronisierten Audiodatei.

---

## Starten des Projekts

Doppelklick auf `StartDubbing.bat`. Das Projekt wird gestartet und zeigt die Hauptschnittstelle mit dem Projektmanagemenü.

---

## Erstellen und Auswählen eines Projekts

Wählen Sie auf der Hauptseite "Projektverwaltung" (Option 0) und erstellen Sie ein neues Projekt. Jedes Projekt ist ein isolierter Arbeitsbereich für ein bestimmtes Video.

Nach der Erstellung wird das Projekt als aktiv definiert und bleibt für nachfolgende Operationen verfügbar.

---

## Operativer Arbeitsablauf

Der Prozess besteht aus 4 Phasen. Jede Phase kann einzeln oder als Teil des vollständigen Ablaufs ausgeführt werden.

| Phase | Vorgang                | Ausgabeverzeichnis                                   |
|-------|------------------------|------------------------------------------------------|
| 1     | Audioextraktion        | `Workspace/projects/{name}/audio_extraction/current/` |
| 2     | Transkription          | `Workspace/projects/{name}/transcripts/current/`      |
| 3     | Übersetzung            | `Workspace/projects/{name}/translated/current/`       |
| 4     | Sprachsynthese (TTS)   | `Workspace/projects/{name}/dubbed/current/`           |

> **Wichtig:** nach der Transkription und nach der Übersetzung wird eine manuelle Überprüfung des generierten Textes empfohlen. Korrektionen verbessern die Qualität der endgültigen Audiodatei und beheben Timing-Unstimmigkeiten.

---

## Eingabevorbereitung

### Videoeingabe

Während der Audioextraktion zeigt das System einen Importdialog, der Ihnen ermöglicht:
1. Das Video von einem externen Speicherort zu nutzen (behält den ursprünglichen Pfad)
2. Das Video in das Projekt zu kopieren (`Workspace/projects/{name}/video_input/`)
3. Das Video in das Projekt zu verschieben

Unterstützte Formate: von ffmpeg unterstützte Formate (mp4, mkv, avi, mov, usw.).

### Direkte Audioeingabe

Wenn Sie bereits extrahiertes Audio haben, können Sie während der Transkription manuell eine Audiodatei aus dem Ordner `Workspace/projects/{name}/audio_input/` oder von einem externen Speicherort auswählen. In diesem Fall kann Phase 1 — Audioextraktion übersprungen werden.

---

## Phase 1 — Audioextraktion

Das System extrahiert die Audiospuren aus dem Video via ffmpeg. Alle extrahierten Audiodateien werden in `Workspace/projects/{name}/audio_extraction/current/` mit den Namen `track_01.wav`, `track_02.wav`, usw. gespeichert.

Für jede Spur wird automatisch eine Metadatendatei generiert (`track_XX_metadata.json`) mit Informationen zu Codec, Abtastrate, Dauer und anderen Eigenschaften.

---

## Phase 2 — Transkription

Das Audio wird in das SRT-Format transkribiert. Die gesprochene Sprache wird automatisch erkannt und kann vor der Transkription im Menü geändert werden. Das Ergebnis wird in `Workspace/projects/{name}/transcripts/current/` gespeichert.

> **Tipp:** überprüfen und korrigieren Sie den transkribierten Text vor der Übersetzung. Fehler in dieser Phase übertragen sich auf alle nachfolgenden Phasen.

---

## Phase 3 — Übersetzung

Die transkribierte SRT-Datei wird in die Zielsprache übersetzt. Die Übersetzung erfolgt vollständig lokal. Erforderliche Modelle werden beim ersten Ausführen für jedes Sprachpaar automatisch heruntergeladen. Das Ergebnis wird in `Workspace/projects/{name}/translated/current/` gespeichert.

Wenn das direkte Sprachpaar nicht verfügbar ist, ist eine Pivot-Übersetzung über Englisch als Zwischensprache für die Zukunft geplant.

> **Tipp:** überprüfen Sie den übersetzten Text vor der Synthese. Manuelle Korrektionen helfen, Timing-Unstimmigkeiten zu beheben.

---

## Phase 4 — Sprachsynthese (TTS)

Der übersetzte Text wird Segment für Segment via den ausgewählten TTS-Anbieter synthetisiert. Die Segmente werden dann in der endgültigen Audiodatei zusammengeführt und in `Workspace/projects/{name}/dubbed/current/` gespeichert.

### TTS-Anbieter

Das System unterstützt derzeit zwei Anbieter:

- **Azure Cognitive Services Speech** — Microsofts Cloud-TTS-Service
- **Google Cloud Text-to-Speech** — Googles Cloud-TTS-Service

Anbieter und Stimme werden direkt im TTS-Menü ausgewählt. Das System bietet eine dedizierte Funktion, um Audiobeispiele der verfügbaren Stimmen vor der Synthese anzuhören.

### Kostenüberwachung

Wenn das TTS-Modul startet, wird eine geschätzte Nutzung automatisch angezeigt. Um den tatsächlichen Verbrauch zu überprüfen, konsultieren Sie direkt das Dashboard Ihres Anbieters.

---

## Oberflächensprache

Die Oberflächensprache wird beim Start ausgewählt und kann jederzeit über das Einstellungsmenü geändert werden, ohne das Projekt neu zu starten.

---

## Projektverwaltung

### Duplizierung

Sie können ein vorhandenes Projekt duplizieren, um eine Kopie mit einem neuen Namen zu erstellen. Nützlich zum Testen von Variationen derselben Quelle.

### Umbenennen

Ein Projekt kann jederzeit über die Projektverwaltung umbenannt werden. Wenn das Projekt aktiv ist, wird der aktive Zeiger automatisch aktualisiert.

### Löschen

Ein Projekt kann gelöscht werden. Wenn die Einstellung `use_trash` aktiviert ist, wird das Projekt in den Papierkorb verschoben; andernfalls wird es dauerhaft gelöscht.

### Ordner Öffnen

Sie können den Ordner eines Projekts direkt im Explorer öffnen, um die generierten Dateien manuell zu überprüfen.

---

## Operationelle Tipps

- Verwenden Sie kurze Projekt- und Dateinamen ohne Leerzeichen oder Sonderzeichen, um Pfadprobleme zu vermeiden.
- Dateien in `Workspace/projects/{name}/video_input/` werden niemals vom System geändert.
- Jede Phase generiert Metadaten (`.json`-Dateien oder `_info.txt`): nützlich zum Verfolgen des Fortschritts oder zur Diagnose von Problemen.
- Wenn der Prozess unterbrochen wird, können Sie ab der nächsten Phase nach der bereits abgeschlossenen fortfahren, indem Sie die Dateien in den Zwischen-Ausgabeverzeichnissen verwenden.
- Verarbeitete Dateien in jeder Phase werden automatisch im `archive/`-Ordner dieser Phase archiviert, um den Verlauf zu erhalten.

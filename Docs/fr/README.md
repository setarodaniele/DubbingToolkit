# DubbingToolkit

> ⚠️ **Avertissement**: Cette documentation a été traduite automatiquement et peut contenir des erreurs ou des imprécisions. Pour une compréhension détaillée, consultez la version en [anglais](../en/README.md).

**DubbingToolkit** est un système de doublage hybride Python + PowerShell qui permet de transcrire, traduire et resynthétiser vocalement des contenus audio/vidéo en plusieurs langues, en utilisant des moteurs TTS professionnels (Azure, Google) et des modèles de transcription locaux (Whisper).

---

## Index de la documentation

| Fichier | Contenu |
|---|---|
| [README.md](README.md) | Cette page — vue d'ensemble générale |
| [installation.md](installation.md) | Prérequis, configuration et mise en route initiale |
| [utilisation.md](utilisation.md) | Guide opérationnel et flux de travail |
| [architecture.md](architecture.md) | Structure du projet, modules et conventions |
| [faq.md](faq.md) | Questions fréquentes et résolution de problèmes |
| [limitations_et_notes.md](limitations_et_notes.md) | Limitations actuelles et fonctionnalités non encore implémentées |
| [credenziali_azure.md](credenziali_azure.md) | Configuration des identifiants Azure |
| [credenziali_google.md](credenziali_google.md) | Configuration des identifiants Google |

---

## Fonctionnement

DubbingToolkit orchestre les principales étapes du doublage — extraction audio, transcription, traduction et synthèse vocale — en réduisant considérablement le travail manuel et en centralisant l'ensemble du processus dans un pipeline unique et contrôlé.

1. **Extraction audio** — Extrait les pistes audio des fichiers vidéo via ffmpeg. Cette étape peut être ignorée si l'audio est déjà disponible.
2. **Transcription** — Transcrit l'audio au format SRT via Whisper.
3. **Traduction** — Traduit les sous-titres SRT dans la langue cible en utilisant des modèles Helsinki-NLP exécutés localement, sans dépendance envers des API externes.
4. **Synthèse vocale (TTS)** — Génère l'audio doublé segment par segment via Azure TTS ou Google TTS, puis assemble les segments dans le fichier audio final.

---

## Langues supportées

L'interface du système est actuellement disponible en 8 langues :

| Code | Langue |
|---|---|
| `it` | Italien |
| `en` | Anglais |
| `es` | Espagnol |
| `de` | Allemand |
| `fr` | Français |
| `pt` | Portugais |
| `ru` | Russe |
| `zh` | Chinois |

Les langues de transcription et de traduction dépendent respectivement de Whisper et des modèles Helsinki-NLP disponibles. Voir `locale/` pour les détails.

---

## Fournisseurs TTS actuellement supportés

- **Azure Cognitive Services Speech** — haute qualité, voix neurales, large couverture linguistique
- **Google Cloud Text-to-Speech** — alternative fiable avec une bonne variété de voix

Les deux fournisseurs nécessitent des identifiants API configurés localement. Voir [installation.md](installation.md).

---

## Point d'entrée

Le projet se lance depuis un seul fichier :

```
StartDubbing.bat
```

Tout le reste est orchestré automatiquement par le Launcher.

---

## État du projet

DubbingToolkit est en développement actif. Certaines fonctionnalités sont déjà opérationnelles dans le pipeline principal ; d'autres sont planifiées comme améliorations futures (segmentation avancée, post-traitement du texte, traduction pivot, etc.). Voir [architecture.md](architecture.md) pour les détails sur l'état des modules.

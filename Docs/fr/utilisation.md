# Guide d'utilisation

Ce guide décrit le flux opérationnel de DubbingToolkit, de la préparation des fichiers d'entrée à l'audio doublé final.

---

## Démarrage du projet

Double-cliquez sur `StartDubbing.bat`. Le projet se lance et présente le menu de gestion des projets.

---

## Création et sélection d'un projet

Depuis l'écran principal, sélectionnez "Gestion des projets" (option 0) et créez un nouveau projet. Chaque projet est un espace de travail isolé pour une vidéo spécifique.

Une fois créé, le projet est défini comme actif et reste disponible pour les opérations ultérieures.

---

## Flux opérationnel

Le processus comprend 4 étapes. Chaque étape peut être exécutée individuellement ou dans le cadre du flux complet.

| Étape | Opération | Dossier de sortie |
|---|---|---|
| 1 | Extraction audio | `Workspace/projects/{nom}/audio_extraction/current/` |
| 2 | Transcription | `Workspace/projects/{nom}/transcripts/current/` |
| 3 | Traduction | `Workspace/projects/{nom}/translated/current/` |
| 4 | Synthèse TTS | `Workspace/projects/{nom}/dubbed/current/` |

> **Important :** une révision manuelle est recommandée après la transcription et après la traduction. Les corrections permettent d'améliorer la qualité de l'audio final.

---

## Préparation des fichiers d'entrée

### Entrée vidéo

Lors de l'extraction audio, le système présente un dialogue d'importation qui permet de :
1. Utiliser la vidéo depuis un emplacement externe (maintient le chemin original)
2. Copier la vidéo dans le projet (`Workspace/projects/{nom}/video_input/`)
3. Déplacer la vidéo dans le projet

Formats supportés : ceux traités par ffmpeg (mp4, mkv, avi, mov, etc.).

### Audio direct

Si vous avez déjà de l'audio extrait, lors de la transcription vous pouvez sélectionner manuellement un fichier audio depuis le dossier `Workspace/projects/{nom}/audio_input/` ou depuis un emplacement externe. Dans ce cas, l'Étape 1 peut être omise.

---

## Étape 1 — Extraction audio

Le système extrait les pistes audio de la vidéo via ffmpeg. Tous les fichiers audio extraits sont enregistrés dans `Workspace/projects/{nom}/audio_extraction/current/` avec les noms `track_01.wav`, `track_02.wav`, etc.

Pour chaque piste, un fichier de métadonnées est généré automatiquement (`track_XX_metadata.json`) contenant des informations sur le codec, la fréquence d'échantillonnage, la durée et autres propriétés.

---

## Étape 2 — Transcription

L'audio est transcrit au format SRT. La langue parlée est détectée automatiquement et peut être modifiée depuis le menu avant de démarrer la transcription. Le résultat est enregistré dans `Workspace/projects/{nom}/transcripts/current/`.

> **Conseil :** avant de procéder à la traduction, examinez et corrigez le texte transcrit. Les erreurs à ce stade se propagent à toutes les étapes ultérieures.

---

## Étape 3 — Traduction

Le fichier SRT transcrit est traduit dans la langue cible. La traduction se fait entièrement en local. Les modèles nécessaires sont téléchargés automatiquement à la première exécution pour chaque paire de langues. Le résultat est enregistré dans `Workspace/projects/{nom}/translated/current/`.

Si la paire de langues directe n'est pas disponible, la traduction pivot via l'anglais comme langue intermédiaire est prévue pour l'avenir.

> **Conseil :** examinez le texte traduit avant de démarrer la synthèse. Les corrections manuelles permettent de gérer les désaccords de synchronisation.

---

## Étape 4 — TTS

Le texte traduit est synthétisé segment par segment via le fournisseur TTS sélectionné. Les segments sont ensuite fusionnés dans le fichier audio final, enregistré dans `Workspace/projects/{nom}/dubbed/current/`.

### Fournisseurs TTS

Le système supporte actuellement deux fournisseurs :

- **Azure Cognitive Services Speech** — service TTS cloud de Microsoft
- **Google Cloud Text-to-Speech** — service TTS cloud de Google

Le fournisseur et la voix sont sélectionnés directement depuis le menu TTS. Le système inclut une fonction dédiée pour écouter des échantillons de voix disponibles avant de démarrer la synthèse.

### Surveillance des coûts

Lorsque le module TTS démarre, une estimation de l'utilisation est automatiquement affichée. Pour vérifier la consommation réelle, consultez directement le panneau de contrôle de votre fournisseur.

---

## Langue de l'interface

La langue de l'interface est sélectionnée au démarrage et peut être modifiée à tout moment depuis le menu des paramètres sans redémarrer le projet.

---

## Gestion des projets

### Duplication

Vous pouvez dupliquer un projet existant pour créer une copie avec un nouveau nom. Utile pour tester des variantes de la même source.

### Renommer

Un projet peut être renommé à tout moment depuis la gestion des projets. Si le projet est actif, le pointeur actif est mis à jour automatiquement.

### Suppression

Un projet peut être supprimé. Si le paramètre `use_trash` est activé, le projet est déplacé à la Corbeille ; sinon il est supprimé définitivement.

### Ouvrir le dossier

Vous pouvez ouvrir le dossier d'un projet directement dans l'Explorateur pour inspecter manuellement les fichiers générés.

---

## Conseils opérationnels

- Utilisez des noms de projet et de fichier courts sans espaces ni caractères spéciaux pour éviter les problèmes de chemins.
- Les fichiers dans `Workspace/projects/{nom}/video_input/` ne sont jamais modifiés par le système.
- Chaque étape génère des métadonnées (fichiers `.json` ou `_info.txt`) : utiles pour suivre la progression ou diagnostiquer les problèmes.
- Si le processus est interrompu, vous pouvez reprendre à partir de l'étape suivante en utilisant les fichiers dans les dossiers de sortie intermédiaires.
- Les fichiers traités à chaque étape sont automatiquement archivés dans le dossier `archive/` de cette étape pour préserver l'historique.

---

## Démarrage du projet

Double-cliquer sur `StartDubbing.bat`. Le projet démarre et présente l'interface principale. Au premier démarrage, toutes les dépendances nécessaires seront installées automatiquement.

---

## Flux opérationnel

Le processus se déroule en 4 étapes. Chaque étape peut être exécutée individuellement ou dans le cadre du flux complet.

| Étape | Opération              | Sortie              |
|-------|------------------------|---------------------|
| 1     | Extraction audio       | `Audio_Extracted/`  |
| 2     | Transcription          | `Transcripts/`      |
| 3     | Traduction             | `Translated/`       |
| 4     | Synthèse vocale (TTS)  | `Dubbed/`           |

> **Important :** après la transcription et après la traduction, une vérification manuelle du texte généré est recommandée. Les corrections permettent d'améliorer la qualité de l'audio final et de gérer les éventuelles incohérences avec le rythme du discours original. Un système automatique de vérification de la cohérence entre le texte et les timecodes audio sera disponible dans une version future.

---

## Préparation des entrées

### Entrée vidéo

Il est possible de placer les fichiers vidéo dans le dossier `Video_Input/` ou de les sélectionner manuellement depuis l'interface.

Formats supportés : ceux gérés par ffmpeg (mp4, mkv, avi, mov, etc.).

### Entrée audio directe

Si l'audio extrait est déjà disponible, il est possible de le placer dans le dossier `Audio_Input/` ou de le sélectionner manuellement. Dans ce cas, l'Étape 1 — Extraction audio peut être ignorée.

---

## Étape 1 — Extraction audio

Le système extrait les pistes audio de la vidéo via ffmpeg. Pour chaque fichier traité, un sous-dossier est automatiquement créé dans `Audio_Extracted/`, contenant les fichiers audio extraits et un fichier `_info.txt` avec les métadonnées de l'extraction.

---

## Étape 2 — Transcription

L'audio est transcrit au format SRT. La langue du discours est détectée automatiquement et peut être modifiée depuis le menu avant de lancer la transcription. Le résultat est sauvegardé dans `Transcripts/`.

> **Conseil :** avant de procéder à la traduction, vérifier et corriger le texte transcrit. Les erreurs à cette étape se répercutent sur toutes les étapes suivantes.

---

## Étape 3 — Traduction

Le fichier SRT transcrit est traduit dans la langue cible. La traduction s'effectue entièrement en local. Les modèles nécessaires sont téléchargés automatiquement à la première exécution pour chaque paire de langues. Le résultat est sauvegardé dans `Translated/`.

Si la paire de langues directe n'est pas disponible, une traduction pivot via l'anglais comme langue intermédiaire est prévue dans une version future.

> **Conseil :** vérifier le texte traduit avant de lancer la synthèse. Les corrections manuelles permettent de gérer les éventuelles incohérences avec le rythme du discours original.

---

## Étape 4 — Synthèse vocale (TTS)

Le texte traduit est synthétisé vocalement, segment par segment, via le fournisseur TTS sélectionné. Les segments sont ensuite assemblés dans le fichier audio final, sauvegardé dans `Dubbed/`.

### Fournisseurs TTS

Le système supporte actuellement deux fournisseurs :

- **Azure Cognitive Services Speech** — service TTS cloud de Microsoft
- **Google Cloud Text-to-Speech** — service TTS cloud de Google

Le fournisseur et la voix se sélectionnent directement depuis le menu TTS. Le système inclut une fonction dédiée pour écouter les échantillons audio des voix disponibles avant de lancer la synthèse.

### Suivi des coûts

Au démarrage du module TTS, une consommation estimée est automatiquement présentée. Pour vérifier la consommation réelle, consulter directement le panneau de son fournisseur.

---

## Langue de l'interface

La langue de l'interface se sélectionne au démarrage et peut être modifiée à tout moment depuis le menu des paramètres sans redémarrer le projet.

---

## Conseils opérationnels

- Utiliser des noms de fichiers courts, sans espaces ni caractères spéciaux, pour éviter les problèmes de chemins.
- Les fichiers dans `Video_Input/` ne sont jamais modifiés par le système.
- Chaque étape génère un fichier `_info.txt` avec les métadonnées : utile pour suivre l'état d'avancement ou diagnostiquer des problèmes.
- En cas d'interruption du processus, il est possible de reprendre depuis l'étape suivant celle déjà complétée, en utilisant les fichiers dans les dossiers de sortie intermédiaires.

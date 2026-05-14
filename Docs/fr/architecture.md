# Architecture et référence technique

Ce document décrit la structure interne du projet, les modules principaux, les conventions de développement et l'état des composants. Il est destiné principalement à ceux qui contribuent au développement ou souhaitent comprendre le fonctionnement interne du système.

---

## Structure des dossiers

```
DubbingToolkit/
├── Audio_Extracted/        Sortie extraction audio (sous-dossiers par fichier)
├── Audio_Input/            Audio d'entrée direct
├── Billing/                Suivi de la consommation et des coûts TTS
├── core/                   Modules de support Python partagés
├── credentials/            Identifiants API (exclus de Git)
├── Dubbed/                 Sortie TTS finale (par fournisseur)
├── Installation/           Runtimes Python locaux (3.10, 3.11)
├── installer/              Système de build et de packaging
├── locale/                 Localisation et gestion des langues
│   ├── Active/             Fichiers JSON de langue actifs (it, en, es, de, fr, pt, ru, zh)
│   └── System/             Métadonnées des langues (Whisper, langues supportées)
├── Logs/                   Journaux opérationnels
├── ps/                     Modules PowerShell (journalisation, messagerie)
├── Repository/             Ressources partagées et modèles locaux
├── Scripts/                Scripts opérationnels et modules Python
│   └── maintenance/        Scripts de maintenance et pipeline de localisation
├── Settings/               Configuration active et de référence
├── Subtitles/              Sous-titres (à implémenter)
├── Temp/                   Fichiers temporaires
├── Tools/                  Binaires externes (ffmpeg)
├── Transcripts/            Transcriptions SRT (sous-dossiers par fichier)
├── Translated/             Traductions SRT (sous-dossiers par fichier)
├── venv/                   Environnement virtuel Python principal
├── Video_Input/            Vidéos source (jamais modifiées)
└── voices/                 Voix TTS disponibles et échantillons audio
```

---

## Chaîne de démarrage

```
StartDubbing.bat
  └→ Scripts/Launcher.ps1
       Active le venv, configuration UTF-8, journaux, chargement de la langue
         └→ Scripts/Regista.py
              Menu principal et orchestration du pipeline
```

Le Launcher gère : la sélection du runtime Python local (`Installation/`), la création/activation du venv, la configuration du système de journaux, le chargement de la langue de l'interface.

`Regista.py` est le coordinateur central : il présente le menu à l'utilisateur et délègue l'exécution aux modules spécifiques pour chaque étape.

---

## Pipeline opérationnel

| Étape | Module | Entrée → Sortie |
|---|---|---|
| 1 — Extraction audio | `Scripts/estrai_tracce.py` | `Video_Input/` → `Audio_Extracted/<ts>/` |
| 2 — Transcription | `Scripts/trascrivi_audio.py` | `Audio_Extracted/` ou `Audio_Input/` → `Transcripts/<ts>/` (SRT) |
| 3 — Traduction | `Scripts/traduci_testo.py` | `Transcripts/` → `Translated/<ts>/` (SRT) |
| 4 — TTS | `Scripts/tts_menu.py` | `Translated/` → `Dubbed/` (MP3/WAV) |

`tts_menu.py` délègue à `tts_azure.py` ou `tts_google.py` selon le fournisseur actif.

---

## Modules core (`core/`)

Ces modules sont partagés par l'ensemble du pipeline. Ils ne doivent pas être appelés directement par l'utilisateur.

### `messages.py`
Système centralisé de messagerie localisée. Lit `Settings/settings.json` → champ `interface_lang` → charge `locale/Active/<lang>.json`.

Utilisation dans les scripts :
```python
from core.messages import Messages
msg = Messages()
print(msg._("chiave_messaggio"))
```

Les clés manquantes produisent le fallback `[MISSING: chiave]` et ne provoquent pas de crash. Toutes les clés manquantes doivent être corrigées avant la mise en production.

### `credentials_manager.py`
Chargement et validation centralisés des identifiants API. C'est le seul point du projet autorisé à lire les fichiers dans `credentials/`. Aucun autre module ne doit accéder directement à ces fichiers.

### `api_check.py`
Vérifie la validité des identifiants avant d'autoriser l'accès au menu TTS. Invoqué automatiquement à l'entrée dans le menu TTS.

### `ui_printer.py` + `ui_colors.py`
Fonctions pour la sortie console avec mise en forme et couleurs. Tous les scripts doivent utiliser ces modules plutôt que `print()` direct, pour garantir une cohérence visuelle.

### `utils_tts.py`
Utilitaires partagés pour le parsing SRT, utilisés par les deux backends TTS.

### `file_selector.py`
Interface pour la sélection de fichiers via menu interactif.

### `input_parsing.py`
Parsing et validation des entrées utilisateur.

---

## Modules Scripts principaux

### `Regista.py`
Orchestrateur principal. Gère le menu de premier niveau et coordonne l'exécution des étapes du pipeline. Point d'entrée Python de l'application.

### `estrai_tracce.py`
Extraction des pistes audio des vidéos via ffmpeg. Génère un sous-dossier dans `Audio_Extracted/` avec les fichiers audio et le fichier `_info.txt`.

### `trascrivi_audio.py`
Transcription audio via Whisper (ou WhisperX, une fois intégré). Sortie au format SRT dans `Transcripts/`.

### `traduci_testo.py`
Traduction SRT via les modèles Helsinki-NLP MarianMT exécutés localement. Sortie dans `Translated/`.

### `tts_dubbing.py` / `tts_menu.py`
Coordination du pipeline TTS. `tts_menu.py` est l'interface utilisateur ; `tts_dubbing.py` gère le flux de génération et d'assemblage des segments.

### `tts_azure.py` / `tts_google.py`
Backends TTS spécifiques à chaque fournisseur. Génèrent les segments audio et les sauvegardent dans `Dubbed/<PROVIDER>/`.

### `tts_merge.py`
Assemblage et synchronisation des segments audio TTS dans le fichier final.

### `tts_config_manager.py`
Gestion des configurations TTS : fournisseur actif, voix sélectionnée, paramètres de synthèse.

### `info_manager.py`
Lecture et écriture du fichier `project_info.json` dans les sous-dossiers horodatés. Garantit la traçabilité de l'état entre les étapes.

### `settings_manager.py`
Lecture, validation et accès aux configurations dans `Settings/settings.json`.

### `monitoraggio_consumo.py`
Accès thread-safe au registre de consommation TTS dans `Billing/consumo_tts.json`.

### `menu_lingue.py` / `menu_lingue_tts.py`
Sélection des langues pour la transcription/traduction et pour le pipeline TTS.

### `menu_voices.py`
Sélection et configuration des voix TTS depuis l'interface.

### `backup_utils.py`
Gestion des sauvegardes et de l'historique des fichiers générés.

---

## Système de localisation

### Structure

```
locale/
├── Active/              Fichiers de langue actifs (runtime)
│   ├── it.json
│   ├── en.json
│   ├── es.json
│   ├── de.json
│   ├── fr.json
│   ├── pt.json
│   ├── ru.json
│   └── zh.json
└── System/
    ├── languages.json           Langues conceptuellement supportées
    └── whisper_languages.json   Langues supportées par Whisper
```

### Règles

- Tous les messages de l'interface Python doivent utiliser `core/messages.py`.
- Tous les fichiers dans `locale/Active/` doivent être synchronisés : une clé présente dans `it.json` doit exister dans tous les autres fichiers de langue.
- Les clés manquantes produisent `[MISSING: key]` à l'exécution — elles ne sont pas admises en environnement stable.
- PowerShell utilise `ps/Messages.psm1` (système équivalent, séparé).

### Pipeline de maintenance de la localisation

Dans `Scripts/maintenance/translation/`, un pipeline complet est disponible pour gérer les fichiers de langue :

| Script | Fonction |
|---|---|
| `LocaleKeyAnalyzer.ps1` | Analyse des clés manquantes et des incohérences entre fichiers |
| `LocaleTranslator.ps1` | Traduction automatique avec protection des espaces réservés |
| `Validate-LocaleJson.ps1` | Validation de la structure et de l'intégrité JSON |
| `Fix-LocaleDuplicates.ps1` | Correction des clés dupliquées |
| `Clean-LocaleUnusedKeys.ps1` | Suppression des clés inutilisées |
| `Extract-Placeholders.ps1` | Extraction et cartographie des espaces réservés |
| `Protect-Placeholders.ps1` | Protection des espaces réservés lors de la traduction automatique |

---

## Configuration (`Settings/settings.json`)

Champs principaux :

```json
{
  "interface_lang": "it",
  "model": "small",
  "Transcript_Audio_Spoken_Lang": "it",
  "Translation_Target_Lang": "en",
  "Dubbing_Lang": "en"
}
```

| Champ | Description |
|---|---|
| `interface_lang` | Langue de l'interface utilisateur |
| `model` | Modèle Whisper à utiliser (`tiny`, `base`, `small`, `medium`, `large`) |
| `Transcript_Audio_Spoken_Lang` | Langue parlée dans l'audio source |
| `Translation_Target_Lang` | Langue cible pour la traduction |
| `Dubbing_Lang` | Langue pour la synthèse TTS |

---

## Gestion des voix TTS

Les voix disponibles sont cataloguées dans `voices/` :

| Fichier | Contenu |
|---|---|
| `voices_azure.json` | Voix Azure filtrées et prêtes à l'emploi |
| `voices_azure_complete.json` | Catalogue complet Azure |
| `voices_google.json` | Voix Google filtrées |
| `voices_google_complete.json` | Catalogue complet Google |
| `voices_index.json` | Index unifié de toutes les voix (Azure + Google) avec métadonnées |

Les échantillons audio des voix (pour écoute) se trouvent dans `voices/voices_output/<provider>/<LANG-CODE>/<voice>.mp3`, s'ils ont été générés via `Scripts/VoicesRepository.py`.

Pour mettre à jour le catalogue des voix depuis les fournisseurs :
```bash
voices/fetch_azure_voices.py
voices/fetch_google_voices.py
```

---

## Système de build et de distribution

Le projet inclut un système de packaging dans `installer/` :

```powershell
installer/build.ps1
```

Les règles d'inclusion/exclusion se trouvent dans :

| Fichier | Rôle |
|---|---|
| `build_include.json` | Ce qui doit être copié, où et dans quel mode |
| `build_exclude.json` | Liste noire globale (tous les modes) |
| `build_exclude_test.json` | Liste noire supplémentaire uniquement en mode TEST (runtime Python, ffmpeg, voices) |
| `build_protected.json` | Chemins copiés verbatim — les règles d'exclusion sont ignorées |
| `build_empty_dirs.json` | Dossiers vides à créer dans le package |

Paramètres disponibles :
```powershell
.\build.ps1              # menu interactif (choix 1/2/3)
.\build.ps1 -Test        # build légère sans composants lourds
.\build.ps1 -Production  # build complète avec confirmation
.\build.ps1 -DryRun      # simulation sans écriture de fichiers
```

La sortie va dans `installer/build_payload/`. Les fichiers d'identifiants réels ne sont jamais inclus dans le build — seuls les fichiers `*.template.json` sont livrés.

---

## Conventions de développement

### Nommage

| Élément | Convention |
|---|---|
| Dossiers (nouveaux) | `minuscolo_underscore` |
| Modules Python | `minuscolo_underscore.py` |
| Classes | `CamelCase` |
| Fonctions et variables | `minuscolo_underscore` |
| Scripts de test | préfixe `test_` obligatoire |

### Structure des scripts

Tous les scripts doivent suivre la structure numérotée définie dans la Section 6 de `RecapDubbing.txt` :

```
# 1. IMPORTS / DEPENDENCIES
# 2. CONFIGURATION – Paths, settings, constants
# 3. UTILITIES – Helper functions
# 4. CORE LOGIC – Main processing
# 5. MAIN EXECUTION – Entry point
```

Chaque script doit inclure un en-tête standard avec le nom, la description, les entrées, les sorties et les notes opérationnelles. Les commentaires dans le code doivent être en anglais.

### Messagerie

- Aucune chaîne de caractères codée en dur dans les modules runtime.
- Tous les messages proviennent des fichiers JSON de localisation via `core/messages.py` (Python) ou `ps/Messages.psm1` (PowerShell).
- Exception : les scripts de bootstrap et les scripts de maintenance peuvent utiliser une sortie non localisée.

### Chemins

Tous les chemins doivent être relatifs à la racine du projet. Aucun chemin absolu dans les modules runtime.

### Fichiers générés

Chaque étape du pipeline qui génère des fichiers crée un sous-dossier au format :
```
<timestamp>_<nom_fichier_source>
```
et inclut un fichier `_info.txt` avec les métadonnées du traitement.

---

## État des composants

| Composant | État |
|---|---|
| Extraction audio | ✅ Opérationnel |
| Transcription Whisper | ✅ Opérationnel |
| Traduction Helsinki-NLP | ✅ Opérationnel |
| TTS Azure | ✅ Opérationnel |
| TTS Google | ✅ Opérationnel |
| Interface multilingue (8 langues) | ✅ Opérationnel |
| Suivi de la consommation TTS | ✅ Opérationnel |
| Système de build/packaging | ✅ Opérationnel |
| Sous-titres (option de menu 5) | ⚠️ Stub — non implémenté |
| Segmentation avancée | ⚠️ Placeholder — hors pipeline |
| WhisperX | ⚠️ Venv préparé, non intégré |
| TTS OpenAI / ElevenLabs | ⚠️ Identifiants présents, non connectés au menu |
| Traduction pivot (langue intermédiaire) | 🔲 Planifié |
| Post-traitement du texte (Traduction→TTS) | 🔲 Planifié |
| Modèle basé sur des projets (dossier unique par projet) | 🔲 Refactoring futur |

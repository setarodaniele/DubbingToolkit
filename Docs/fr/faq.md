# FAQ et résolution de problèmes

---

## Démarrage et environnement

**Le projet ne démarre pas avec `StartDubbing.bat`.**

Une cause fréquente est le blocage de l'exécution des scripts PowerShell.
Ouvrir PowerShell en tant qu'administrateur et exécuter :
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
Puis réessayer le démarrage.

---

**Le venv est corrompu ou ne s'active pas.**

Supprimer manuellement le dossier `venv/` à l'intérieur du dossier du projet. Au prochain démarrage via `StartDubbing.bat`, le Launcher détectera l'absence du venv et le recréera automatiquement.

---

**Erreur `[MISSING: key]` dans l'interface.**

Indique qu'une clé est absente dans le fichier de localisation actif. Ce n'est pas bloquant mais réduit la clarté de l'interface. Signaler la clé manquante pour permettre sa correction.

---

## Identifiants et API

**Le système signale des identifiants Azure invalides.**

Vérifier que `credentials/azure_speech_credentials.json` contient les champs `subscription` (clé API) et `region` (ex. `westeurope`). Utiliser `credentials/azure_speech_credentials.template.json` comme référence pour la structure correcte.

---

**Le système signale des identifiants Google invalides.**

`credentials/google_speech_credentials.json` doit être le fichier JSON complet d'un compte de service GCP avec le rôle Cloud Text-to-Speech activé. Vérifier que le fichier n'est pas tronqué ou malformé.

> Des guides dédiés à la création des identifiants Azure et Google sont disponibles dans le même dossier que cette documentation.

---

## Transcription

**La transcription produit des résultats imprécis ou dans la mauvaise langue.**

Spécifier manuellement la langue source via le menu des langues avant de lancer la transcription. Les langues disponibles sont listées dans le menu de sélection de langue.

---

**La transcription est très lente.**

La vitesse dépend du modèle Whisper sélectionné et du matériel disponible. Le modèle se sélectionne directement dans le menu de transcription avant de lancer le processus.

| Modèle | Vitesse | Qualité |
|---|---|---|
| `tiny` | Très élevée | Basique |
| `base` | Élevée | Correcte |
| `small` | Moyenne | Bonne |
| `medium` | Basse | Élevée |
| `large` | Très basse | Maximale |

Sur CPU sans GPU dédié, même le modèle `small` peut être lent sur des fichiers longs.

---

**La transcription s'interrompt avec une erreur de mémoire.**

Des fichiers audio très longs chargés entièrement en RAM peuvent poser problème sur des systèmes avec peu de mémoire. Envisager de découper le fichier audio en segments plus courts avant la transcription.

---

## Traduction

**La paire de langues souhaitée n'est pas disponible.**

Toutes les paires linguistiques ne disposent pas d'un modèle Helsinki-NLP direct. Les paires supportées sont listées dans le menu de sélection de langue. La traduction via langue pivot (anglais comme intermédiaire) est planifiée mais pas encore implémentée.

---

**Le texte traduit contient des erreurs ou sonne peu naturel.**

Les modèles Helsinki-NLP sont des modèles de traduction automatique et peuvent produire des imprécisions, notamment sur des expressions idiomatiques ou des termes techniques. Le post-traitement du texte est planifié comme amélioration future.

---

## Synthèse TTS

**Le TTS génère de l'audio avec des pauses ou des rythmes peu naturels.**

Vérifier la voix sélectionnée dans le menu TTS. Les voix neurales (Azure Neural, Google WaveNet) produisent des résultats significativement meilleurs que les voix standard. Il est possible d'écouter les échantillons audio avant de lancer la synthèse.

---

**La sortie TTS est silencieuse ou ne contient que du bruit.**

Ouvrir le fichier SRT traduit dans `Translated/` avec un éditeur de texte et vérifier qu'il contient des segments valides avec du texte non vide.

---

**Le suivi de la consommation ne se met pas à jour.**

La consommation est enregistrée dans `Billing/consumo_tts.json`. Si le fichier est bloqué ou corrompu, en faire une sauvegarde, le supprimer — il sera recréé automatiquement à la prochaine utilisation.

---

## Fichiers et dossiers

**Je ne trouve pas la sortie générée.**

Chaque étape crée un sous-dossier au format `<timestamp>_<nom_fichier>` dans son répertoire de sortie. Chercher dans :
- `Audio_Extracted/` pour l'audio extrait
- `Transcripts/` pour les transcriptions SRT
- `Translated/` pour les traductions SRT
- `Dubbed/<PROVIDER>/` pour l'audio doublé final

Le fichier `_info.txt` dans chaque sous-dossier indique les détails du traitement.

---

**J'ai déplacé le projet et il ne fonctionne plus.**

Supprimer manuellement le dossier `venv/`. Au prochain démarrage via `StartDubbing.bat`, le Launcher recréera le venv au nouvel emplacement.

---

## Build et distribution

**Les identifiants API ne sont pas inclus dans le package de distribution.**

C'est le comportement correct. Les identifiants Azure et Google ne sont jamais inclus dans le package pour des raisons de sécurité. Ils doivent être renseignés manuellement dans le dossier `credentials/` sur chaque machine après l'installation, en suivant la structure des fichiers template.

---

## Questions générales

**Est-il possible d'utiliser le projet sans connexion internet ?**

Partiellement. La transcription (Whisper) et la traduction (Helsinki-NLP) fonctionnent hors ligne une fois les modèles téléchargés. La synthèse TTS (Azure, Google) nécessite une connexion internet car elle utilise des API cloud.

---

**Est-il possible d'ajouter de nouvelles langues à l'interface ?**

Oui. De nouvelles langues seront ajoutées progressivement au fil du temps. Pour demander une langue spécifique, il est possible de contacter directement le projet. Ceux qui souhaitent l'ajouter eux-mêmes doivent :

1. Créer le fichier `locale/Active/<code_langue>.json` en suivant la structure des autres fichiers de langue existants
2. Ajouter la nouvelle langue dans `locale/System/languages.json`

Les deux étapes sont nécessaires : sans la seconde, la langue ne sera pas reconnue par le système.

---

**Le projet supporte-t-il le traitement en lot de plusieurs vidéos ?**

Pour l'instant, le flux est conçu pour un fichier à la fois. Il est possible de préparer plusieurs fichiers et de les traiter en séquence, mais il n'existe pas de mode batch automatique. Cette fonctionnalité est envisagée pour des développements futurs.

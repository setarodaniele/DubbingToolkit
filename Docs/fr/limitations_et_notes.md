# Limitations et notes

Ce document recense de manière transparente les limitations actuelles de DubbingToolkit, les fonctionnalités pas encore implémentées et les comportements connus qui pourraient ne pas correspondre aux attentes. Le projet est en développement actif et ces limitations sont destinées à être résolues progressivement.

---

## Paramètres non persistants

Les paramètres ne sont pas sauvegardés d'une session à l'autre. À chaque démarrage, le système repart des valeurs par défaut et demande la langue de l'interface. Toutes les autres préférences — fournisseur TTS, voix, modèle Whisper, langues de transcription et de traduction — doivent être resélectionnées à chaque fois. La persistance des paramètres est planifiée comme amélioration future.

---

## Aucun mode batch

Le flux est conçu pour traiter un fichier à la fois. Il n'existe pas de mode permettant de traiter automatiquement plusieurs fichiers en séquence. Cette fonctionnalité est envisagée pour des développements futurs.

---

## Qualité de la traduction

La traduction utilise des modèles Helsinki-NLP exécutés localement. La qualité peut être inférieure à celle de services cloud de traduction professionnelle, notamment sur les expressions idiomatiques, les termes techniques ou les textes avec une ponctuation irrégulière. Une vérification manuelle du texte traduit est toujours recommandée avant de procéder à la synthèse.

---

## Aucune vérification automatique des timecodes

Après la traduction, le texte peut être plus long ou plus court que l'original, créant des incohérences avec les timecodes du discours dans la vidéo. Il n'existe actuellement aucun système automatique de vérification ou d'adaptation. La gestion des timecodes nécessite une intervention manuelle sur le fichier SRT traduit. Un système automatique de vérification et d'adaptation est planifié comme amélioration future.

---

## Transcription : détection automatique de la langue

Whisper détecte automatiquement la langue du discours, mais sur un audio bruité, avec un accent marqué ou de mauvaise qualité, il peut commettre des erreurs. Dans ces cas, il est nécessaire de spécifier manuellement la langue avant la transcription. Un système d'évaluation du niveau de confiance de la détection est planifié comme amélioration future.

---

## Transcription : gestion de la mémoire

Les fichiers audio très longs sont chargés entièrement en mémoire lors de la transcription. Sur des systèmes avec peu de RAM, cela peut entraîner des ralentissements ou des interruptions. Le traitement par blocs est planifié comme amélioration future.

---

## WhisperX non intégré

L'environnement pour WhisperX est préparé mais pas encore intégré dans le pipeline principal. Seul Whisper standard est actuellement utilisé.

---

## Sous-titres non disponibles

La fonction d'export de sous-titres est présente dans le menu mais pas encore implémentée. En la sélectionnant, le système ne produit aucune sortie.

---

## Fournisseurs TTS supplémentaires non connectés

Seuls Azure et Google sont actuellement supportés. L'intégration de fournisseurs supplémentaires, dont OpenAI et ElevenLabs, est prévue dans une version future.

---

## Traduction pivot non disponible

Si la paire de langues directe source→cible n'est pas disponible dans les modèles Helsinki-NLP, la traduction n'est pas possible. La traduction via langue pivot (anglais comme intermédiaire) est planifiée mais pas encore implémentée.

---

## Portabilité limitée

Le projet peut être déplacé vers un autre emplacement, mais cela nécessite la reconstruction de l'environnement virtuel après chaque déplacement. Ce n'est pas un système entièrement portable.

---

## Traitement séquentiel

Les étapes du pipeline sont exécutées en séquence. Il n'est pas possible de paralléliser le traitement de plusieurs fichiers ou d'exécuter des étapes simultanément.

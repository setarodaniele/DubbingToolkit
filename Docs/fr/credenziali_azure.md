> ⚠️ **ATTENTION — Sécurité des identifiants**
>
> Les identifiants contenus dans ce fichier sont strictement personnels et directement liés à votre facturation.
> Toute personne qui en prendrait possession pourrait utiliser le service à vos frais, générant potentiellement des coûts élevés.
>
> - Ne jamais partager ce fichier avec qui que ce soit
> - Ne pas le télécharger sur des dépôts publics (GitHub, etc.)
> - Ne pas l'envoyer par e-mail ou messagerie
> - En cas de perte ou de compromission, révoquer immédiatement la clé depuis le portail du fournisseur et en générer une nouvelle

# Configuration des identifiants Azure

Ce guide décrit comment obtenir et configurer les identifiants pour Azure Cognitive Services Speech, nécessaires pour la synthèse vocale via le fournisseur Azure.

> Un guide vidéo détaillé sur la création des identifiants Azure sera disponible dans une version future.

---

## Fichier des identifiants

Le fichier à renseigner est :

```
credentials/azure_speech_credentials.json
```

La structure requise est la suivante :

```json
{
  "subscription": "YOUR_AZURE_SPEECH_KEY",
  "region": "YOUR_AZURE_REGION"
}
```

Un fichier template avec cette structure est déjà disponible dans le projet :

```
credentials/azure_speech_credentials.template.json
```

Le copier, le renommer en supprimant l'extension `.template` et renseigner les champs.

---

## Champs requis

### `subscription`

La clé API du service Azure Cognitive Services Speech. Elle se trouve dans le portail Azure dans la section **Clés et point de terminaison** de la ressource Speech.

### `region`

La région Azure associée à la ressource (ex. `westeurope`, `eastus`, `northeurope`). Elle doit correspondre exactement à la région sélectionnée lors de la création de la ressource.

---

## Comment obtenir les identifiants

1. Accéder au [portail Azure](https://portal.azure.com)
2. Rechercher ou créer une ressource **Speech** (Cognitive Services)
3. Dans la ressource créée, ouvrir la section **Clés et point de terminaison**
4. Copier l'une des deux clés disponibles (`KEY 1` ou `KEY 2`) — les deux fonctionnent
5. Noter la **Localisation/Région** de la ressource — correspond à la valeur `region`

---

## Exemple renseigné

```json
{
  "subscription": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
  "region": "westeurope"
}
```

---

## Notes

- Les clés Azure ont une longueur de 32 caractères hexadécimaux.
- Le service Speech nécessite un plan actif (un plan gratuit avec limite mensuelle de caractères est disponible).
- En cas d'identifiants invalides, le système le signale au démarrage du module TTS.

> ⚠️ **ATTENTION — Sécurité des identifiants**
>
> Les identifiants contenus dans ce fichier sont strictement personnels et directement liés à votre facturation.
> Toute personne qui en prendrait possession pourrait utiliser le service à vos frais, générant potentiellement des coûts élevés.
>
> - Ne jamais partager ce fichier avec qui que ce soit
> - Ne pas le télécharger sur des dépôts publics (GitHub, etc.)
> - Ne pas l'envoyer par e-mail ou messagerie
> - En cas de perte ou de compromission, révoquer immédiatement la clé depuis le portail du fournisseur et en générer une nouvelle

# Configuration des identifiants Google

Ce guide décrit comment obtenir et configurer les identifiants pour Google Cloud Text-to-Speech, nécessaires pour la synthèse vocale via le fournisseur Google.

> Un guide vidéo détaillé sur la création des identifiants Google Cloud sera disponible dans une version future.

---

## Fichier des identifiants

Le fichier à renseigner est :

```
credentials/google_speech_credentials.json
```

La structure requise est la suivante :

```json
{
  "type": "service_account",
  "project_id": "YOUR_PROJECT_ID",
  "private_key_id": "YOUR_PRIVATE_KEY_ID",
  "private_key": "YOUR_PRIVATE_KEY",
  "client_email": "YOUR_CLIENT_EMAIL",
  "client_id": "YOUR_CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "YOUR_CLIENT_CERT_URL",
  "universe_domain": "googleapis.com"
}
```

Un fichier template avec cette structure est déjà disponible dans le projet :

```
credentials/google_speech_credentials.template.json
```

Le copier, le renommer en supprimant l'extension `.template` et renseigner les champs avec les valeurs de son compte de service.

---

## Champs requis

Les champs avec une valeur fixe (`type`, `auth_uri`, `token_uri`, `auth_provider_x509_cert_url`, `universe_domain`) ne doivent pas être modifiés — ils sont identiques pour tous les comptes Google Cloud.

Les champs à renseigner sont :

| Champ | Description |
|---|---|
| `project_id` | ID du projet Google Cloud |
| `private_key_id` | ID de la clé privée du compte de service |
| `private_key` | Clé privée au format PEM (avec les en-têtes `-----BEGIN/END PRIVATE KEY-----`) |
| `client_email` | E-mail du compte de service (ex. `nom@projet.iam.gserviceaccount.com`) |
| `client_id` | ID numérique du compte de service |
| `client_x509_cert_url` | URL du certificat X509 du compte de service |

---

## Comment obtenir les identifiants

1. Accéder à la [Google Cloud Console](https://console.cloud.google.com)
2. Créer ou sélectionner un projet existant
3. Activer l'API **Cloud Text-to-Speech** dans la section **API et services**
4. Aller dans **IAM et administration → Comptes de service**
5. Créer un nouveau compte de service avec le rôle **Cloud Text-to-Speech Agent** (ou équivalent avec accès TTS)
6. Dans l'onglet **Clés** du compte de service, créer une nouvelle clé au format **JSON**
7. Télécharger le fichier JSON généré — il contient tous les champs nécessaires déjà renseignés
8. Copier le contenu du fichier téléchargé dans `credentials/google_speech_credentials.json`

---

## Notes

- Le fichier JSON téléchargé depuis Google Cloud Console est déjà au format correct et peut être utilisé directement sans modification.
- Conserver le fichier en lieu sûr : la clé privée ne peut pas être récupérée après la création.
- En cas d'identifiants invalides ou expirés, générer une nouvelle clé depuis la Console et mettre à jour le fichier.
- Le service Cloud Text-to-Speech prévoit un plan gratuit avec limite mensuelle de caractères.

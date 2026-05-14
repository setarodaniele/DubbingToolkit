> ⚠️ **ACHTUNG — Sicherheit der Anmeldedaten**
> Nicht weitergeben, nicht in öffentliche Repositorys hochladen. Bei Kompromittierung sofort widerrufen.

# Google-Anmeldedaten konfigurieren

## Datei

```
credentials/google_speech_credentials.json
```

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

## Auszufüllende Felder

| Feld | Beschreibung |
|---|---|
| `project_id` | GCP-Projekt-ID |
| `private_key_id` | ID des privaten Schlüssels |
| `private_key` | PEM-Schlüssel |
| `client_email` | E-Mail-Adresse des Dienstkontos |
| `client_id` | Numerische ID |
| `client_x509_cert_url` | X509-Zertifikat-URL |

## So erhalten Sie die Anmeldedaten

1. [Google Cloud Console](https://console.cloud.google.com) öffnen
2. **Cloud Text-to-Speech API** aktivieren
3. IAM → Dienstkonto → Mit Rolle **Cloud Text-to-Speech Agent** erstellen
4. Schlüssel → JSON erstellen → Herunterladen
5. Nach `credentials/google_speech_credentials.json` kopieren

## Hinweise

- JSON liegt bereits im richtigen Format vor
- Privater Schlüssel ist nicht wiederherstellbar
- Kostenloser Tarif verfügbar

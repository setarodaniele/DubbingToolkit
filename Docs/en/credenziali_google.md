> ⚠️ **WARNING — Credential Security**
>
> The credentials contained in this file are strictly personal and directly linked to your billing.
> Anyone who obtains them could use the service at your expense, potentially generating significant costs.
>
> - Never share this file with anyone
> - Do not upload it to public repositories (GitHub, etc.)
> - Do not send it via email or chat
> - If lost or compromised, immediately revoke the key from the provider portal and generate a new one

# Google Credentials Configuration

This guide describes how to obtain and configure credentials for Google Cloud Text-to-Speech, required for speech synthesis via the Google provider.

> A detailed video guide on how to create Google Cloud credentials will be available in the future.

---

## Credentials File

The file to fill in is:

```
credentials/google_speech_credentials.json
```

The required structure is as follows:

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

A template file with this structure is already available in the project:

```
credentials/google_speech_credentials.template.json
```

Copy it, rename it by removing the `.template` extension, and fill in the fields with your service account values.

---

## Required Fields

The fields with fixed values (`type`, `auth_uri`, `token_uri`, `auth_provider_x509_cert_url`, `universe_domain`) should not be modified — they are the same for all Google Cloud accounts.

The fields to fill in are:

| Field | Description |
|---|---|
| `project_id` | Google Cloud project ID |
| `private_key_id` | Service account private key ID |
| `private_key` | Private key in PEM format (including `-----BEGIN/END PRIVATE KEY-----` headers) |
| `client_email` | Service account email (e.g. `name@project.iam.gserviceaccount.com`) |
| `client_id` | Service account numeric ID |
| `client_x509_cert_url` | Service account X509 certificate URL |

---

## How to Obtain Credentials

1. Sign in to the [Google Cloud Console](https://console.cloud.google.com)
2. Create or select an existing project
3. Enable the **Cloud Text-to-Speech** API under **APIs & Services**
4. Go to **IAM & Admin → Service Accounts**
5. Create a new service account with the **Cloud Text-to-Speech Agent** role (or equivalent with TTS access)
6. In the **Keys** tab of the service account, create a new key in **JSON** format
7. Download the generated JSON file — it contains all required fields already filled in
8. Copy the contents of the downloaded file to `credentials/google_speech_credentials.json`

---

## Notes

- The JSON file downloaded from Google Cloud Console is already in the correct format and can be used directly without modifications.
- Store the file securely: the private key cannot be recovered after creation.
- If credentials are invalid or expired, generate a new key from the Console and update the file.
- The Cloud Text-to-Speech service offers a free tier with a monthly character limit.

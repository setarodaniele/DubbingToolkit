> ⚠️ **ATTENZIONE — Sicurezza delle credenziali**
> 
> Le credenziali contenute in questo file sono strettamente personali e direttamente collegate alla tua fatturazione. 
> Chiunque ne entrasse in possesso potrebbe utilizzare il servizio a tue spese, potenzialmente generando costi elevati.
> 
> - Non condividere mai questo file con nessuno
> - Non caricarlo su repository pubblici (GitHub, ecc.)
> - Non inviarlo via email o chat
> - In caso di perdita o compromissione, revocare immediatamente la chiave dal portale del provider e generarne una nuova

# Configurazione credenziali Google

Questa guida descrive come ottenere e configurare le credenziali per Google Cloud Text-to-Speech, necessarie per la sintesi vocale tramite il provider Google.

> In futuro sarà disponibile una guida video dettagliata su come creare le credenziali Google Cloud.

---

## File di credenziali

Il file da compilare è:

```
credentials/google_speech_credentials.json
```

La struttura richiesta è la seguente:

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

Un file template con questa struttura è già disponibile nel progetto:

```
credentials/google_speech_credentials.template.json
```

Copiarlo, rinominarlo rimuovendo l'estensione `.template` e compilare i campi con i valori del proprio service account.

---

## Campi richiesti

I campi con valore fisso (`type`, `auth_uri`, `token_uri`, `auth_provider_x509_cert_url`, `universe_domain`) non vanno modificati — sono uguali per tutti gli account Google Cloud.

I campi da compilare sono:

| Campo | Descrizione |
|---|---|
| `project_id` | ID del progetto Google Cloud |
| `private_key_id` | ID della chiave privata del service account |
| `private_key` | Chiave privata in formato PEM (inclusi header `-----BEGIN/END PRIVATE KEY-----`) |
| `client_email` | Email del service account (es. `nome@progetto.iam.gserviceaccount.com`) |
| `client_id` | ID numerico del service account |
| `client_x509_cert_url` | URL del certificato X509 del service account |

---

## Come ottenere le credenziali

1. Accedere alla [Google Cloud Console](https://console.cloud.google.com)
2. Creare o selezionare un progetto esistente
3. Abilitare l'API **Cloud Text-to-Speech** nella sezione **API e servizi**
4. Andare in **IAM e amministrazione → Account di servizio**
5. Creare un nuovo account di servizio con il ruolo **Cloud Text-to-Speech Agent** (o equivalente con accesso TTS)
6. Nella scheda **Chiavi** dell'account di servizio, creare una nuova chiave in formato **JSON**
7. Scaricare il file JSON generato — contiene tutti i campi necessari già compilati
8. Copiare il contenuto del file scaricato in `credentials/google_speech_credentials.json`

---

## Note

- Il file JSON scaricato da Google Cloud Console è già nel formato corretto e può essere usato direttamente senza modifiche.
- Conservare il file in modo sicuro: la chiave privata non può essere recuperata dopo la creazione.
- In caso di credenziali non valide o scadute, generare una nuova chiave dalla Console e aggiornare il file.
- Il servizio Cloud Text-to-Speech prevede un piano gratuito con limite mensile di caratteri.

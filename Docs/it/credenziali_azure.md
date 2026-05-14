> ⚠️ **ATTENZIONE — Sicurezza delle credenziali**
> 
> Le credenziali contenute in questo file sono strettamente personali e direttamente collegate alla tua fatturazione. 
> Chiunque ne entrasse in possesso potrebbe utilizzare il servizio a tue spese, potenzialmente generando costi elevati.
> 
> - Non condividere mai questo file con nessuno
> - Non caricarlo su repository pubblici (GitHub, ecc.)
> - Non inviarlo via email o chat
> - In caso di perdita o compromissione, revocare immediatamente la chiave dal portale del provider e generarne una nuova

# Configurazione credenziali Azure

Questa guida descrive come ottenere e configurare le credenziali per Azure Cognitive Services Speech, necessarie per la sintesi vocale tramite il provider Azure.

> In futuro sarà disponibile una guida video dettagliata su come creare le credenziali Azure.

---

## File di credenziali

Il file da compilare è:

```
credentials/azure_speech_credentials.json
```

La struttura richiesta è la seguente:

```json
{
  "subscription": "YOUR_AZURE_SPEECH_KEY",
  "region": "YOUR_AZURE_REGION"
}
```

Un file template con questa struttura è già disponibile nel progetto:

```
credentials/azure_speech_credentials.template.json
```

Copiarlo, rinominarlo rimuovendo l'estensione `.template` e compilare i campi.

---

## Campi richiesti

### `subscription`

La chiave API del servizio Azure Cognitive Services Speech. Si trova nel portale Azure nella sezione **Chiavi ed endpoint** della risorsa Speech.

### `region`

La regione Azure associata alla risorsa (es. `westeurope`, `eastus`, `northeurope`). Deve corrispondere esattamente alla regione selezionata durante la creazione della risorsa.

---

## Come ottenere le credenziali

1. Accedere al [portale Azure](https://portal.azure.com)
2. Cercare o creare una risorsa **Speech** (Cognitive Services)
3. Nella risorsa creata, aprire la sezione **Chiavi ed endpoint**
4. Copiare una delle due chiavi disponibili (`KEY 1` o `KEY 2`) — entrambe funzionano
5. Annotare la **Località/Area** della risorsa — corrisponde al valore `region`

---

## Esempio compilato

```json
{
  "subscription": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
  "region": "westeurope"
}
```

---

## Note

- Le chiavi Azure hanno una lunghezza di 32 caratteri esadecimali.
- Il servizio Speech richiede un piano attivo (è disponibile un piano gratuito con limite mensile di caratteri).
- In caso di credenziali non valide, il sistema lo segnala all'avvio del modulo TTS.

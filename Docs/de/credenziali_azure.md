> ⚠️ **ACHTUNG — Sicherheit der Anmeldedaten**
> Anmeldedaten sind streng vertraulich. Nicht weitergeben, nicht in öffentliche Repositorys hochladen. Bei Kompromittierung sofort widerrufen.

# Azure-Anmeldedaten konfigurieren

## Datei

```
credentials/azure_speech_credentials.json
```

```json
{
  "subscription": "YOUR_AZURE_SPEECH_KEY",
  "region": "YOUR_AZURE_REGION"
}
```

Vorlage: `credentials/azure_speech_credentials.template.json`

## Felder

- **`subscription`**: API-Schlüssel aus **Schlüssel und Endpunkt** im Azure-Portal
- **`region`**: z. B. `westeurope`, `eastus`, `northeurope`

## So erhalten Sie die Anmeldedaten

1. [Azure-Portal](https://portal.azure.com) öffnen
2. **Speech**-Ressource (Cognitive Services) aufrufen
3. **Schlüssel und Endpunkt** → KEY 1 oder KEY 2 kopieren
4. Region notieren

## Beispiel

```json
{
  "subscription": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
  "region": "westeurope"
}
```

## Hinweise

- 32 hexadezimale Zeichen
- Kostenloser Tarif verfügbar
- Ungültige Anmeldedaten werden beim TTS-Start gemeldet

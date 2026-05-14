> ⚠️ **WARNING — Credential Security**
>
> The credentials contained in this file are strictly personal and directly linked to your billing.
> Anyone who obtains them could use the service at your expense, potentially generating significant costs.
>
> - Never share this file with anyone
> - Do not upload it to public repositories (GitHub, etc.)
> - Do not send it via email or chat
> - If lost or compromised, immediately revoke the key from the provider portal and generate a new one

# Azure Credentials Configuration

This guide describes how to obtain and configure credentials for Azure Cognitive Services Speech, required for speech synthesis via the Azure provider.

> A detailed video guide on how to create Azure credentials will be available in the future.

---

## Credentials File

The file to fill in is:

```
credentials/azure_speech_credentials.json
```

The required structure is as follows:

```json
{
  "subscription": "YOUR_AZURE_SPEECH_KEY",
  "region": "YOUR_AZURE_REGION"
}
```

A template file with this structure is already available in the project:

```
credentials/azure_speech_credentials.template.json
```

Copy it, rename it by removing the `.template` extension, and fill in the fields.

---

## Required Fields

### `subscription`

The API key for the Azure Cognitive Services Speech service. It can be found in the Azure portal under the **Keys and Endpoint** section of the Speech resource.

### `region`

The Azure region associated with the resource (e.g. `westeurope`, `eastus`, `northeurope`). It must exactly match the region selected when the resource was created.

---

## How to Obtain Credentials

1. Sign in to the [Azure portal](https://portal.azure.com)
2. Search for or create a **Speech** (Cognitive Services) resource
3. In the created resource, open the **Keys and Endpoint** section
4. Copy one of the two available keys (`KEY 1` or `KEY 2`) — both work
5. Note the **Location/Region** of the resource — this corresponds to the `region` value

---

## Filled-In Example

```json
{
  "subscription": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
  "region": "westeurope"
}
```

---

## Notes

- Azure keys are 32 hexadecimal characters long.
- The Speech service requires an active plan (a free plan with a monthly character limit is available).
- If credentials are invalid, the system reports this when the TTS module is launched.

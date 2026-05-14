# Credentials

This folder contains credential files required by the TTS and translation providers.
Real credential files are NOT included in the installer — only templates are shipped.

## Setup

Copy the relevant template file, rename it by removing `.template` from the name,
and fill in your actual API keys or service account data.

## Files

| Template file                          | Final file name                    | Provider             |
|----------------------------------------|------------------------------------|----------------------|
| azure_speech_credentials.template.json | azure_speech_credentials.json      | Azure Cognitive TTS  |
| google_speech_credentials.template.json| google_speech_credentials.json     | Google Cloud TTS     |

## Providers without template (manual setup)

The following providers require credentials that must be created manually:

- **ElevenLabs** → `ElevenLab.json` — requires an ElevenLabs API key
- **OpenAI** → `openai_key.json` — requires an OpenAI API key
- **HuggingFace** → `HuggingFace.json` — requires a HuggingFace API token
- **Google Cloud Translate** → `GoogleCloudTranslate.json` — requires a GCP service account

Refer to the provider's documentation for the exact JSON format expected.

## Security

- Never commit real credential files to version control.
- Real credential files are listed in `.gitignore`.
- The installer only ships template files from this folder.

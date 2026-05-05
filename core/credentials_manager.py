# =========================================================
# credentials_manager.py
# =========================================================
# Gestione centralizzata lettura credenziali provider
# =========================================================

import os
import json
from core.messages import Messages

# Carica messaggi (locale/Active/it.json o lingua impostata)
messages = Messages()

# =========================================================
# Funzione generica: carica credenziali da file JSON
# =========================================================
def load_credentials(json_path, required_keys):
    """
    Carica credenziali da un file JSON e verifica la presenza
    delle chiavi richieste.

    :param json_path: percorso file JSON
    :param required_keys: lista chiavi obbligatorie
    :return: dizionario con chiavi richieste
    """
    if not os.path.isfile(json_path):
        raise FileNotFoundError(messages.cred_mgr_file_not_found.format(json_path))

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    missing = [key for key in required_keys if key not in data]
    if missing:
        raise ValueError(messages.cred_mgr_missing_keys.format(missing))

    return data


# =========================================================
# Funzione di alto livello: ottieni credenziali per provider
# =========================================================
def get_provider_credentials(provider_name):
    """
    Restituisce le credenziali di un provider sotto forma di dizionario.
    Usa il file JSON corrispondente nella cartella 'credentials' nella root progetto.
    """

    # Root del progetto
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cred_folder = os.path.join(project_root, "credentials")

    # Configurazione provider supportati
    providers = {
        "azure": {
            "file": "azure_speech_credentials.json",
            "required_keys": ["subscription", "region"]
        },
        "google": {
            "file": "google_speech_credentials.json",
            "required_keys": [
                "type",
                "project_id",
                "private_key_id",
                "private_key",
                "client_email",
                "client_id",
                "auth_uri",
                "token_uri",
                "auth_provider_x509_cert_url",
                "client_x509_cert_url",
                "universe_domain"
            ]
        }
    }

    provider_key = provider_name.lower()

    if provider_key not in providers:
        raise ValueError(messages.cred_mgr_unsupported_provider.format(provider_name))

    provider_data = providers[provider_key]

    cred_file = os.path.join(cred_folder, provider_data["file"])
    required_keys = provider_data["required_keys"]

    return load_credentials(cred_file, required_keys)
    
def provider_credentials_exist(provider_name):
    """
    Restituisce True se le credenziali del provider esistono e sono valide.
    Non lancia eccezioni, restituisce solo True/False.
    """
    try:
        get_provider_credentials(provider_name)
        return True
    except (FileNotFoundError, ValueError):
        return False


def get_active_providers():
    """
    Restituisce la lista dei provider TTS disponibili con credenziali valide.
    """
    providers = []
    for p in ["google", "azure"]:
        if provider_credentials_exist(p):
            providers.append(p)
    return providers
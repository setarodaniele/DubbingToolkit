# =========================================================
# 1. api_check.py (pulito con messaggi JSON)
# =========================================================

import os
import sys
import json

# =========================================================
# 1.1 Aggiunta percorso progetto al path
# =========================================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.messages import Messages

# =========================================================
# 2. Classe APIStatus
# =========================================================
class APIStatus:
    """Gestisce la disponibilità delle chiavi API per TTS basandosi solo sui file JSON."""

    # =========================================================
    # 2.1 Configurazione provider TTS
    # =========================================================
    PROVIDERS = {
        "azure": {
            "file": "azure_speech_credentials.json",
            "required_keys": ["subscription", "region"]
        },
        "google": {
            "file": "google_speech_credentials.json",
            "required_keys": [
                "type", "project_id", "private_key_id", "private_key", "client_email",
                "client_id", "auth_uri", "token_uri", "auth_provider_x509_cert_url",
                "client_x509_cert_url", "universe_domain"
            ]
        }
    }

    # =========================================================
    # 2.2 Inizializzazione oggetto
    # =========================================================
    def __init__(self, messages: Messages):
        self.messages = messages
        self.file_status = {}  # stato dei file di credenziali
        self._check_credential_files()  # verifica file JSON

    # =========================================================
    # 2.2.1 _check_credential_files()
    # =========================================================
    def _check_credential_files(self):
        """Verifica presenza file credenziali e chiavi richieste."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cred_folder = os.path.join(project_root, "credentials")

        for provider, info in self.PROVIDERS.items():
            path = os.path.join(cred_folder, info["file"])
            if not os.path.isfile(path):
                self.file_status[provider] = self.messages.API_chek_FileNotFound.format(file_path=path)
                continue

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            missing = [k for k in info["required_keys"] if k not in data]
            if missing:
                self.file_status[provider] = self.messages.API_chek_MissingKeys.format(keys=missing)
            else:
                self.file_status[provider] = self.messages.API_chek_AllKeysPresent

    # =========================================================
    # 2.2.2 is_tts_available()
    # =========================================================
    def is_tts_available(self):
        """Restituisce True se almeno un provider ha tutte le chiavi presenti."""
        for provider_status in self.file_status.values():
            if provider_status == self.messages.API_chek_AllKeysPresent:
                return True
        return False

    # =========================================================
    # 2.2.3 missing_keys_message()
    # =========================================================
    def missing_keys_message(self):
        """Restituisce lista dei provider con file o chiavi mancanti."""
        missing = [p for p, status in self.file_status.items() if status != self.messages.API_chek_AllKeysPresent]
        if missing:
            return self.messages.API_chek_CredentialsMissing, missing
        return None, None

    # =========================================================
    # 2.2.4 get_active_providers()
    # =========================================================
    def get_active_providers(self):
        """Restituisce la lista dei provider TTS che hanno tutte le chiavi presenti."""
        return [p for p, s in self.file_status.items() if s == self.messages.API_chek_AllKeysPresent]

    # =========================================================
    # 2.2.5 is_tts_available()
    # =========================================================
    def is_tts_available(self):
        """Restituisce True se almeno un provider TTS ha tutte le chiavi presenti."""
        return bool(self.get_active_providers())
 
# =========================================================
# 3. Funzione helper globale: check_tts_status()
# ========================================================= 
# 3.1 check_tts_status()
def check_tts_status():
    messages = Messages()
    status = APIStatus(messages)
    return {
        "tts_available": status.is_tts_available(),
        "active_providers": status.get_active_providers(),
        #"missing_info": status.missing_keys_message()
    }
        
# =========================================================
# 3. Debug / test standalone pulito (stringhe hardcoded ok)
# =========================================================
if __name__ == "__main__":
    print("=== Debug API TTS ===")
    result = check_tts_status()

    print("TTS disponibile:", result["tts_available"])
    print("Provider attivi:", result["active_providers"])
    if result["missing_info"][0]:
        print(result["missing_info"][0], "→", result["missing_info"][1])

    # Stampa dettagli file_status per debug approfondito
    status = APIStatus(Messages())
    print("\n=== Stato file credenziali ===")
    for provider, s in status.file_status.items():
        print(f"{provider}: {s}")
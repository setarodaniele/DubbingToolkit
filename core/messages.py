# =========================================================
# messages.py
# Shared localization wrapper class
# =========================================================

import json
from pathlib import Path

class Messages:
    """
    Wrapper per i dati di localizzazione JSON.
    - La lingua principale è quella definita in settings.json (interface_lang).
    - Se non definita, la lingua di default sarà inglese.
    - Chiavi mancanti restituiranno [MISSING: key] per evidenziare traduzioni mancanti.
    """

    def __init__(self, settings_file: Path = None, locale_folder: Path = None):
        # Percorso ai file delle lingue
        self.locale_folder = locale_folder or Path.cwd() / "Locale" / "Active"
        self.settings_file = settings_file or Path.cwd() / "Settings" / "settings.json"

        # Legge settings e imposta lingua principale
        if self.settings_file.exists():
            with self.settings_file.open("r", encoding="utf-8-sig") as f:
                settings = json.load(f)
            self.interface_lang = settings.get("interface_lang", "en")
        else:
            self.interface_lang = "en"

        # Carica file della lingua attiva
        active_lang_file = self.locale_folder / f"{self.interface_lang}.json"
        if active_lang_file.exists():
            with active_lang_file.open("r", encoding="utf-8-sig") as f:
                self._data = json.load(f)
        else:
            self._data = {}

        # Carica fallback inglese (solo se la lingua principale non è inglese)
        if self.interface_lang != "en":
            fallback_file = self.locale_folder / "en.json"
            if fallback_file.exists():
                with fallback_file.open("r", encoding="utf-8-sig") as f:
                    self._fallback_data = json.load(f)
            else:
                self._fallback_data = {}
        else:
            self._fallback_data = {}

    def __getattr__(self, key):
        """
        Restituisce il valore della chiave.
        Se manca nella lingua attiva, lascia [MISSING: key].
        """
        if key in self._data:
            return self._data[key]
        elif key in self._fallback_data:
            # Non usiamo fallback per non nascondere missing keys
            return f"[MISSING: {key}]"
        else:
            return f"[MISSING: {key}]"
'''
    def reload_language(self, new_lang: str = None):
        """
        Aggiorna la lingua dei messaggi.
        - Se new_lang è None, prende quella da settings.json.
        """
        if new_lang:
            self.interface_lang = new_lang
        elif self.settings_file.exists():
            with self.settings_file.open("r", encoding="utf-8-sig") as f:
                settings = json.load(f)
            self.interface_lang = settings.get("interface_lang", "en")

        active_lang_file = self.locale_folder / f"{self.interface_lang}.json"
        if active_lang_file.exists():
            with active_lang_file.open("r", encoding="utf-8-sig") as f:
                self._data = json.load(f)
        else:
            self._data = {}

        # Aggiorna fallback inglese
        if self.interface_lang != "en":
            fallback_file = self.locale_folder / "en.json"
            if fallback_file.exists():
                with fallback_file.open("r", encoding="utf-8-sig") as f:
                    self._fallback_data = json.load(f)
            else:
                self._fallback_data = {}
        else:
            self._fallback_data = {}
'''
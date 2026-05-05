# =========================================================
# Regista.py
# =========================================================


import sys
import os

# Aggiunge la cartella principale del progetto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.messages import Messages  # classe centrale
from core.api_check import check_tts_status 

from pathlib import Path
import json
from colorama import Fore, Style, init
from SilenziaWarning import *
from estrai_tracce import estrai_tracce
from trascrivi_audio import trascrivi_audio
from traduci_testo import traduci_testo
from maintenance.pulizia_debug import pulizia_file_test
from monitoraggio_consumo import ConsumoTTS
import settings_manager
from settings_manager import default_setting
from core.logger import logger



init()
'''
# Load default settings at startup
default_setting(messages=None, preserve_interface_lang=True)

# =========================================================
# Set locale for proper number/character formatting
# =========================================================
try:
    locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Italian_Italy.1252')
'''

# =========================================================
# Title display
# =========================================================
def mostra_titolo_menu(messages, titolo_key):
    """Show a menu title with separators and color."""
    titolo = getattr(messages, titolo_key, f"[MISSING: {titolo_key}]")
    print("\n" + Fore.CYAN + "-"*28)
    print(titolo)
    print("-"*28 + Style.RESET_ALL)


# =========================================================
# TTS Engine Selection
# =========================================================
def scegli_motore_tts(messages):
    consumo_google = ConsumoTTS(motore="google")
    consumo_azure = ConsumoTTS(motore="azure")

    print(Fore.YELLOW + "\n" + messages.RegistaTTSConsumption)
    print(f"Google: {consumo_google.dati['google'][consumo_google.data_oggi]} caratteri "
          f"({consumo_google.percentuale_consumo():.1f}% franchigia)")
    print(f"Azure: {consumo_azure.dati['azure'][consumo_azure.data_oggi]} caratteri "
          f"({consumo_azure.percentuale_consumo():.1f}% franchigia)" + Style.RESET_ALL)

    while True:
        print("\n" + messages.RegistaTTSSelect)
        print(messages.RegistaTTSGoogle)
        print(messages.RegistaTTSAzure)
        scelta = input("Scelta (1 o 2): ").strip()
        if scelta == "1":
            return "google"
        elif scelta == "2":
            return "azure"
        else:
            print(messages.RegistaTTSChoiceInvalid)




# =========================================================
# Menu display
# =========================================================
def menu(messages, tts_enabled):
    """Display main workflow menu options."""
    print(messages.RegistaMenuOption1)
    print(messages.RegistaMenuOption2)
    print(messages.RegistaMenuOption3)

    # Opzione 4: colore a seconda della disponibilità TTS
    if tts_enabled:
        print(messages.RegistaMenuOption4)
    else:
        print(Fore.LIGHTBLACK_EX + messages.RegistaMenuOption4 + " (Disabilitato)" + Style.RESET_ALL)

    # Sottotitoli non disponibili → grigio e messaggio "To do"
    print(Fore.LIGHTBLACK_EX + messages.RegistaMenuOption5 + " (To do)" + Style.RESET_ALL)

    print(messages.RegistaMenuOption8)
    print(messages.RegistaMenuOption9)
    print(messages.RegistaMenuOption0)

    scelta = input(messages.RegistaMenuPrompt + " ").strip()

    # Blocca selezione sottotitoli
    if scelta == "5":
        print(Fore.YELLOW + messages.RegistaMenuOption5Disabled + Style.RESET_ALL)
        return None

    # Blocca selezione opzione 4 se TTS disabilitato
    if scelta == "4" and not tts_enabled:
        print(Fore.YELLOW + messages.RegistaMenuOption4Disabled + Style.RESET_ALL)
        return None

    return scelta

# =========================================================
# Main program loop
# =========================================================
def main(messages):
    RESET_FILE = Path.cwd() / "Settings" / "reset.json"
    SETTINGS_FILE = Path.cwd() / "Settings" / "settings.json"

    def load_reset_flags():
        with RESET_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_reset_flags(data):
        with RESET_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Controllo primo avvio
    '''
    reset_flags = load_reset_flags()
    if reset_flags.get("first_launch", True):
        default_setting(messages)
        reset_flags["first_launch"] = False
        save_reset_flags(reset_flags)
        '''

    # Carica settings all’avvio
    with SETTINGS_FILE.open("r", encoding="utf-8-sig") as f:
        settings = json.load(f)
    
    # =====================================================
    # Controllo disponibilità TTS (aggiornato con JSON e colori)
    # =====================================================
    tts_status = check_tts_status()

    if tts_status["tts_available"]:
        # Messaggio in verde dal JSON o da Messages
        print(Fore.GREEN + "\n---------------------------------------" + Style.RESET_ALL)
        print(Fore.GREEN + messages.RegistaTTSActive + Style.RESET_ALL)
        print(Fore.GREEN + messages.RegistaTTSProviders, tts_status["active_providers"])
        print(Fore.GREEN + "---------------------------------------" + Style.RESET_ALL)
        tts_enabled = True
    else:
        # Messaggio in giallo o rosso dal JSON o da Messages
        print(Fore.YELLOW + messages.RegistaTTSDisabled + Style.RESET_ALL)
        #if tts_status["missing_info"][0]:
         #   print(Fore.YELLOW + tts_status["missing_info"][0] + " → " + str(tts_status["missing_info"][1]) + Style.RESET_ALL)
        tts_enabled = False

    logger.info("Regista", "main", "Application started",
                context={"tts_available": tts_enabled,
                         "providers": tts_status.get("active_providers", [])})

    # =====================================================
    # Main loop invariato
    # =====================================================        
    while True:
        mostra_titolo_menu(messages, "MenuFlussoLavoroTitle")
        scelta = menu(messages, tts_enabled)

        if scelta is not None:
            logger.info("Regista", "main", f"Menu option selected: {scelta}")

        if scelta == '1':
            estrai_tracce(messages, settings)
        elif scelta == '2':
            trascrivi_audio(messages, settings)
        elif scelta == '3':
            traduci_testo(messages, settings)
        elif scelta == '4':
            if tts_enabled:
                from tts_menu import tts_menu 
                tts_menu(messages, settings)
            else:
                print(Fore.YELLOW + messages.RegistaMenuOption4Disabled + Style.RESET_ALL)
        elif scelta == '5':
            import Sottotitoli
            Sottotitoli.main(settings=settings)
        elif scelta == '8':
            new_messages = settings_manager.main(messages)  # main returns either None or a new Messages
            if new_messages is not None:
                messages = new_messages  # replace old Messages with updated one
            # Reload settings after possible modifications
            with SETTINGS_FILE.open("r", encoding="utf-8-sig") as f:
                settings = json.load(f)
        elif scelta == '9':
            pulizia_file_test()
        elif scelta == '0':
            print(messages.RegistaExit)
            logger.info("Regista", "main", "User exited application")
            break
        else:
            print(messages.RegistaChoiceInvalid)


# =========================================================
# Entry point - Load messages and start main loop
# =========================================================
if __name__ == "__main__":
    default_setting(messages=None, preserve_interface_lang=True)
    messages = Messages()
    try:
        main(messages)
    finally:
        logger.close_session()


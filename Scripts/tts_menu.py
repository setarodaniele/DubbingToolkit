# =========================================================
# tts_menu.py
# =========================================================

import os
import sys
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from core.credentials_manager import get_active_providers
from core.ui_printer import print_menu_header, print_info, print_success, offer_open_folder
from core.workspace_manager import WorkspaceManager
from monitoraggio_consumo import ConsumoTTS
from tts_dubbing import tts_dubbing

from tts_config_manager import (
    config_status,
    aggiorna_file_srt,
    aggiorna_lingua,
    aggiorna_motore_tts,
    aggiorna_voce,
    aggiorna_formato_output
)

# =========================================================
# UTIL
# =========================================================
def clear_console():
    """Pulisce la console a seconda del sistema operativo."""
    os.system("cls" if os.name == "nt" else "clear")

# =========================================================
# FORMAT FIELD (recupero dati campi menu)
# =========================================================
def format_field(value, fallback, disabled_msg=None):
    """Formatta il campo per la visualizzazione nel menu.
    Colore verde se OK, giallo se non selezionato, grigio se disabilitato."""
    if value:
        if hasattr(value, "name"):
            value = value.name
        return f"{Fore.GREEN}[OK]{Style.RESET_ALL} - {value}"
    elif disabled_msg:
        return f"{Style.DIM}[{disabled_msg}]{Style.RESET_ALL}"
    else:
        return f"{Fore.YELLOW}[{fallback}]{Style.RESET_ALL}"

# =========================================================
# MAIN MENU
# =========================================================
def tts_menu(messages, settings=None):

    while True:
        print("\n" * 5)

        # Project context header
        ws = WorkspaceManager.get_active()
        if ws is not None:
            C, Y, R = Fore.CYAN, Fore.YELLOW, Style.RESET_ALL
            print(C + "-" * 54 + R)
            print(C + getattr(messages, "DUBBING_MenuTitle", "DOPPIAGGIO") + R)
            print(Y + getattr(messages, "RegistaWorkspaceNamed", "[Progetto: {0}]").format(ws.name) + R)
            print(C + "-" * 54 + R)
        else:
            print_menu_header(messages.DUBBING_MenuTitle)

        # =========================================================
        # BLOCCO 1: RIEPILOGO CONSUMO SISTEMA TTS
        # =========================================================
        # 1.1: Calcolo mese corrente
        current_month = datetime.now().strftime("%Y-%m")

        # 1.2: Recupero dati consumo Google e Azure
        consumo_google = ConsumoTTS(motore="google")
        consumo_azure = ConsumoTTS(motore="azure")
        google_chars = consumo_google.dati["google"].get(current_month,0)
        azure_chars = consumo_azure.dati["azure"].get(current_month,0)
        google_percent = consumo_google.percentuale_consumo()
        azure_percent = consumo_azure.percentuale_consumo()
        google_cost = consumo_google.costo_stimato()
        azure_cost = consumo_azure.costo_stimato()

        # 1.3: Stampa riepilogo consumo con messaggi da file JSON
        active_providers = get_active_providers()  # lista provider con credenziali valide
        print()
        print(f"{messages.DUBBING_InfoBox_StatusTitle}: {current_month}")
        print("-----------------------------------")
        # Google
        if "google" in active_providers:
            print("Google")
            print(f"{messages.DUBBING_InfoBox_CharactersUsed}: {google_chars}")
            print(f"{messages.DUBBING_InfoBox_PercentageUsed}: {google_percent:.2f}%")
            print(f"{messages.DUBBING_InfoBox_EstimatedCost}: €{google_cost:.2f}")
        else:
            print(f"{Style.DIM}{messages.TTS_Menu_GoogleNotAvailable}{Style.RESET_ALL}")
        print("-----------------------------------")
        # Azure
        if "azure" in active_providers:
            print("Azure")
            print(f"{messages.DUBBING_InfoBox_CharactersUsed}: {azure_chars}")
            print(f"{messages.DUBBING_InfoBox_PercentageUsed}: {azure_percent:.2f}%")
            print(f"{messages.DUBBING_InfoBox_EstimatedCost}: €{azure_cost:.2f}")
        else:
            print(f"{Style.DIM}{messages.TTS_Menu_AzureNotAvailable}{Style.RESET_ALL}")
        print("----------------------------------")

        # 1.4: Messaggio istruzioni configurazione TTS
        print()
        print_info(messages.DUBBING_ConfigPrompt)

        # =========================================================
        # BLOCCO 2: STATO CONFIGURAZIONE
        # =========================================================
        # 2.1: Verifica se tutti i parametri necessari sono selezionati
        stato_pronto = (
            config_status.get("file_srt") and
            config_status.get("language_code") and
            config_status.get("display_name") and
            config_status.get("output_format")
        )
        stato = messages.DUBBING_StatusReady if stato_pronto else messages.DUBBING_StatusNotReady
        colore = Fore.GREEN if stato_pronto else Fore.YELLOW

        # 2.2: Stampa stato menu
        print(messages.DUBBING_MenuDivider)
        print(f"{messages.DUBBING_LabelStatus}: {colore}{stato}{Style.RESET_ALL}")
        print(messages.DUBBING_MenuDivider)

        # =========================================================
        # BLOCCO 3: MENU CONFIGURAZIONE PARAMETRI
        # =========================================================
        # 3.1: Etichette dinamiche menu
        labels = [
            messages.DUBBING_LabelFileSRT,
            messages.DUBBING_LabelLanguage,
            messages.DUBBING_LabelVoice,
            messages.DUBBING_LabelEngine,
            messages.DUBBING_LabelOutputFormat
        ]
        max_label_len = max(len(l) for l in labels)

        # =========================
        # BLOCCO 3.2: Preparazione valori da stampare
        # =========================
        file_display = format_field(config_status.get("file_srt"), messages.DUBBING_LabelNotSelected)

        # Lingua
        if not config_status.get("file_srt"):
            lingua_display = format_field(None, None, messages.DUBBING_LabelNotAvailableSelectSRT)
            lingua_enabled = False
        else:
            language_code = config_status.get("language_code")
            if language_code:
                lang_key = f"LANG_{language_code.lower()}"
                lingua_nome = getattr(messages, lang_key, language_code.capitalize())
                source = config_status.get("language_source", "manual")
                nota = messages.DUBBING_LabelLanguageAuto if source == "auto" else messages.DUBBING_LabelLanguageManual
                display_text = f"{lingua_nome} ({nota})"
                lingua_display = format_field(display_text, messages.DUBBING_LabelNotSelected)
            else:
                lingua_display = format_field(None, messages.DUBBING_LabelNotSelected)
            lingua_enabled = True

        # Voce
        if not config_status.get("file_srt") or not config_status.get("language_code"):
            voce_display = format_field(None, None, messages.DUBBING_LabelVoiceLocked)
            voce_enabled = False
        else:
            voce_display = format_field(config_status.get("display_name"), messages.DUBBING_LabelNotSelected)
            voce_enabled = True

        # Motore TTS
        motore_display = format_field(config_status.get("provider"), messages.DUBBING_LabelNotSelected)

        # Formato output
        output_display = format_field(config_status.get("output_format"), messages.DUBBING_LabelNotSelected) + " (mp3/wav)"

        # =========================
        # BLOCCO 3.3: Stampa menu opzioni
        # =========================
        print(f"1. {labels[0]:<{max_label_len}} : {file_display}")
        print(f"2. {labels[1]:<{max_label_len}} : {lingua_display}")
        print(f"3. {labels[2]:<{max_label_len}} : {voce_display}")
        print(f"4. {labels[3]:<{max_label_len}} : {motore_display}")
        print(f"5. {labels[4]:<{max_label_len}} : {output_display}")

        # 3.4: Divider e avvio doppiaggio
        print(messages.DUBBING_MenuDivider)
        if stato_pronto:
            print(f"6. {messages.DUBBING_LabelStart}")
        else:
            print(f"{Style.DIM}6. {messages.DUBBING_LabelStart} ({messages.DUBBING_Alert_NotReady}){Style.RESET_ALL}")
        print(f"0. {messages.DUBBING_LabelExit}")

        # =========================================================
        # BLOCCO 4: INPUT UTENTE
        # =========================================================
        scelta = input(messages.DUBBING_PromptSelect).strip()

        # 4.1: Gestione selezioni
        if scelta == "1":
            aggiorna_file_srt(messages)
        elif scelta == "2":
            if lingua_enabled:
                aggiorna_lingua(messages)
            else:
                print(Fore.YELLOW + messages.DUBBING_LabelNotAvailableSelectSRT + Style.RESET_ALL)
                input(messages.DUBBING_PromptContinue)
        elif scelta == "3":
            if voce_enabled:
                aggiorna_voce(messages)  # aggiorna config_status['display_name'] e eventualmente provider
                # Aggiorno solo i display relativi a voce e motore
                voce_display = format_field(config_status.get("display_name"), messages.DUBBING_LabelNotSelected)
                motore_display = format_field(config_status.get("provider"), messages.DUBBING_LabelNotSelected)
            else:
                print(Fore.YELLOW + messages.DUBBING_LabelVoiceLocked + Style.RESET_ALL)
                input(messages.DUBBING_PromptContinue)
        elif scelta == "4":
            aggiorna_motore_tts(messages)
        elif scelta == "5":
            aggiorna_formato_output(messages)
        elif scelta == "6":
            if stato_pronto:
                result = tts_dubbing(config_status, settings=settings, messages=messages)
                print_success(f"{messages.DUBBING_LabelOutputResult}: {result}")
                ws = WorkspaceManager.get_active()
                track_id = config_status.get("track_id")
                if ws and track_id:
                    offer_open_folder(ws.stage_current("dubbed", track_id), messages)
                else:
                    input(messages.DUBBING_PromptContinue)
            else:
                print(Fore.YELLOW + messages.DUBBING_Alert_NotReady + Style.RESET_ALL)
                input(messages.DUBBING_PromptContinue)
        elif scelta == "0":
            return

    
    
# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    
    from core.messages import Messages
    messages = Messages()
    tts_menu(messages)
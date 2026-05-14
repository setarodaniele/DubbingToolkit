# =========================================================
# check_settings_monitor.py
# Monitora settings.json in tempo reale e stampa modifiche evidenziate.
# Premere F5 per forzare un refresh completo dei valori.
# =========================================================

import json
import time
from pathlib import Path
from colorama import Fore, Style, init
import msvcrt  # per intercettare tasti funzione su Windows

# Inizializza Colorama
init(autoreset=True)

# Percorso al file settings.json
SETTINGS_FILE = Path(__file__).parent.parent.parent / "Settings" / "settings.json"

# Stato interno per confronto
_previous_content = None
_previous_mtime = None

def load_settings():
    """Legge settings.json e ritorna come lista di stringhe."""
    with open(SETTINGS_FILE, "r", encoding="utf-8-sig") as f:
        content = f.read()
    return content.splitlines()

def display_changes(force_reload=False):
    """Confronta la versione corrente con quella precedente e stampa modifiche."""
    global _previous_content
    global _previous_mtime

    try:
        current_content = load_settings()
        current_mtime = SETTINGS_FILE.stat().st_mtime
    except FileNotFoundError:
        print(Fore.RED + f"Settings file not found: {SETTINGS_FILE}" + Style.RESET_ALL)
        return

    # Primo avvio o refresh forzato
    if _previous_content is None or force_reload:
        print(Fore.CYAN + "[Initial load of settings.json]" + Style.RESET_ALL)
        for line in current_content:
            print(line)
    
    else:
        if current_content == _previous_content:
            if current_mtime != _previous_mtime:
                # File sovrascritto senza modifiche
                print(Fore.CYAN + "[File salvato ma contenuto invariato]" + Style.RESET_ALL)
            # Altrimenti non fare nulla: nessuna modifica, nessun salvataggio
        else:
            # File modificato
            modifications = []
            max_lines = max(len(_previous_content), len(current_content))
            for i in range(max_lines):
                prev_line = _previous_content[i] if i < len(_previous_content) else ""
                curr_line = current_content[i] if i < len(current_content) else ""
                if curr_line != prev_line:
                    modifications.append(curr_line)

            for line in modifications:
                print(Fore.YELLOW + line + Style.RESET_ALL)

    # Aggiorna lo stato
    _previous_content = current_content
    _previous_mtime = current_mtime


def monitor_settings(poll_interval=1.0):
    """Loop infinito per monitorare il file con intervallo definito (in secondi)."""
    global _previous_content
    print(Fore.GREEN + f"Monitoring {SETTINGS_FILE} for changes..." + Style.RESET_ALL)

    while True:
        display_changes()

        # Controllo tasti funzione senza bloccare
        if msvcrt.kbhit():
            key = msvcrt.getch()
            # Tasti funzione (F1-F12) generano due byte: b'\x00' o b'\xe0' + codice tasto
            if key in (b'\x00', b'\xe0'):
                key2 = msvcrt.getch()
                if key2 == b';':  # F5
                    print(Fore.CYAN + "[Refresh completo del file premuto F5]" + Style.RESET_ALL)
                    _previous_content = None  # forza reload completo
                    display_changes(force_reload=True)

        time.sleep(poll_interval)

if __name__ == "__main__":
    try:
        monitor_settings()
    except KeyboardInterrupt:
        print(Fore.RED + "\nMonitor interrotto manualmente." + Style.RESET_ALL)

    input("\nPremi Invio per chiudere...")

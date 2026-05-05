# pulizia_debug.py

import os
import shutil
from colorama import Fore, Style, init

init()

def trova_file_e_cartelle_da_pulire(cartelle, estensioni, eccezioni_file=None):
    da_cancellare = []
    cartelle_da_cancellare = []
    if eccezioni_file is None:
        eccezioni_file = []

    for cartella in cartelle:
        if not os.path.exists(cartella):
            continue
        for root, dirs, files in os.walk(cartella):
            for file in files:
                full_path = os.path.join(root, file)
                if any(file.endswith(ext) for ext in estensioni) and full_path not in eccezioni_file:
                    da_cancellare.append(full_path)
            for d in dirs:
                cartelle_da_cancellare.append(os.path.join(root, d))
    return da_cancellare, cartelle_da_cancellare

def filtra_cartelle(cartelle):
    # Ordina per lunghezza (da più corta a più lunga)
    cartelle = sorted(cartelle, key=lambda x: len(x))
    cartelle_filtrate = []

    for c in cartelle:
        # Se c è sottocartella di una già inserita, la salto
        if any(c.startswith(parent + os.sep) for parent in cartelle_filtrate):
            continue
        cartelle_filtrate.append(c)

    return cartelle_filtrate

def pulizia_file_test():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    cartelle_da_pulire = [
        os.path.join(base_dir, "Audio-it"),
        os.path.join(base_dir, "Audio-en"),
        os.path.join(base_dir, "srt"),
        os.path.join(base_dir, "Output"),
        # os.path.join(base_dir, "VideoDaDoppiare"),
        # os.path.join(base_dir, "Logs"),
        # os.path.join(base_dir, "Temp")
    ]
    estensioni = ['.mp3', '.srt', '.bak', '.wav', '.mkv']

    # Eccezione esplicita per il file video originale da non cancellare
    eccezioni = [os.path.join(base_dir, "VideoDaDoppiare", "VideoDaDoppiare.mkv")]

    print(Fore.YELLOW + " Analisi preliminare dei file e cartelle da pulire...\n" + Style.RESET_ALL)
    files, dirs = trova_file_e_cartelle_da_pulire(cartelle_da_pulire, estensioni, eccezioni)

    # Filtraggio cartelle per non tentare cancellazioni duplicate
    dirs = filtra_cartelle(dirs)

    if not files and not dirs:
        print(Fore.GREEN + " Nessun file o cartella da eliminare trovati." + Style.RESET_ALL)
        return

    print(Fore.CYAN + " File che verranno eliminati:" + Style.RESET_ALL)
    for f in files:
        print(f"  - {f}")

    print(Fore.CYAN + "\n Cartelle che verranno eliminate:" + Style.RESET_ALL)
    for d in dirs:
        print(f"  - {d}")

    conferma = input(Fore.YELLOW + "\n Procedere con l'eliminazione? (s/n): " + Style.RESET_ALL).strip().lower()
    if conferma != 's':
        print(Fore.RED + " Pulizia annullata dall'utente." + Style.RESET_ALL)
        return

    print(Fore.YELLOW + "\n Eliminazione file in corso..." + Style.RESET_ALL)
    for f in files:
        try:
            os.remove(f)
            print(Fore.GREEN + f" [RIMOSSO FILE] {f}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f" [ERRORE FILE] {f}: {e}" + Style.RESET_ALL)

    print(Fore.YELLOW + "\n Eliminazione cartelle in corso..." + Style.RESET_ALL)
    for d in dirs:
        try:
            shutil.rmtree(d)
            print(Fore.GREEN + f" [RIMOSSA CARTELLA] {d}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f" [ERRORE CARTELLA] {d}: {e}" + Style.RESET_ALL)

    print(Fore.CYAN + "\n [✔] Pulizia completata." + Style.RESET_ALL)

if __name__ == "__main__":
    pulizia_file_test()

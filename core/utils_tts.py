# =========================================================
# core/utils_tts.py
# =========================================================
# Funzioni generiche per gestione TTS
# =========================================================

import re
import os

# =========================================================
# Parsing SRT
# =========================================================
def parse_srt(file_path):
    """
    Restituisce lista di tuple (filename, testo, start_time, end_time) per ciascun blocco SRT.
    Il filename sarà generato come "HH-MM-SS-ms_HH-MM-SS-ms" per indicare inizio e fine frase.
    """
    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Divide i blocchi separati da una o più righe vuote
    blocchi = re.split(r'\n\n+', content.strip())
    
    for blocco in blocchi:
        righe = blocco.splitlines()
        if len(righe) >= 3:
            time_line = righe[1].strip()
            # Match per inizio e fine timestamp
            match = re.match(
                r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})',
                time_line
            )
            if match:
                start_time = f"{match.group(1)}-{match.group(2)}-{match.group(3)}-{match.group(4)}"
                end_time = f"{match.group(5)}-{match.group(6)}-{match.group(7)}-{match.group(8)}"
                timestamp_filename = f"{start_time}_{end_time}"
                testo = " ".join(righe[2:]).strip()
                entries.append((timestamp_filename, testo, start_time, end_time))
    
    return entries

# =========================================================
# Genera nome file a partire da un timestamp
# =========================================================
def genera_nome_file(timestamp, estensione="wav"):
    return f"{timestamp}.{estensione}"

# =========================================================
# Assicurati che la cartella esista
# =========================================================
def assicurati_cartella(path):
    os.makedirs(path, exist_ok=True)
    return path

# =========================================================
# Conteggio caratteri da file SRT (per monitoraggio consumo)
# =========================================================
def count_characters(file_input):
    """
    Calcola il numero totale di caratteri presenti nei blocchi di un file SRT.
    Utilizza il parser SRT interno (parse_srt) per estrarre le entry e somma
    la lunghezza del testo di ciascun blocco.
    Parametri:
        file_input (str | Path): percorso del file SRT
    Ritorna:
        int: numero totale di caratteri presenti nel file
    Note:
        - Restituisce 0 se il file è vuoto o non parsabile
        - Non solleva eccezioni: funzione pensata per uso sicuro lato orchestratore
    """
    try:
        entries = parse_srt(file_input)
        if not entries:
            return 0
        return sum(len(entry[1]) for entry in entries)
    except Exception:
        return 0
        
  # =========================================================
# Stampa riepilogo TTS
# =========================================================
def print_tts_summary(data):
    """
    Stampa un riepilogo sintetico del doppiaggio TTS.
    
    Parametri:
        data (dict) con chiavi obbligatorie:
            - input_file : percorso file sorgente
            - provider   : provider TTS ("google", "azure", ecc.)
            - language   : codice lingua o descrizione
            - voice      : voce TTS utilizzata
            - segments   : numero di segmenti elaborati
            - total_chars: numero totale caratteri nel file
            - new_chars  : numero di caratteri aggiunti in questo run
            - cost       : costo stimato del run
            - output_path: percorso cartella/file di output
            - status     : stato run ("COMPLETATO", "ERRORE", ecc.)
            - duration   : opzionale, durata totale audio
    """
    print("\n----------------------------")
    print("Doppiaggio completato")
    print("----------------------------\n")

    print(f"File sorgente : {data['input_file']}")
    print(f"Provider      : {data['provider']}")
    print(f"Lingua        : {data['language']}")
    print(f"Voce TTS      : {data['voice']}")

    print(f"\nSegmenti      : {data['segments']}")
    print(f"Caratteri     : {data['total_chars']} (+{data['new_chars']})")
    print(f"Costo run     : €{data['cost']:.4f}")

    if data.get("duration"):
        print(f"Durata audio  : {data['duration']}")

    print(f"\nOutput        : {data['output_path']}")
    print(f"\nStato         : {data['status']}")
    print("----------------------------")    
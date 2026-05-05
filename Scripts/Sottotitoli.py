# Sottotitoli.py

import os
import shutil
from SilenziaWarning import *
import whisper
import torch
from colorama import Fore, Style, init

init()

# ---------------- VARIABILE MODIFICABILE ----------------
# Durata (in secondi) del sottotitolo dopo la fine della frase
BUFFER_POST_FRASE = 1.5
# --------------------------------------------------------

MODELLI_WHISPER = {
    "1": "tiny",
    "2": "base",
    "3": "small",
    "4": "medium",
    "5": "large"
}

def scegli_modello():
    print("\nScegli il modello Whisper (default=small):")
    for k, v in MODELLI_WHISPER.items():
        print(f"{k}. {v}")
    scelta = input("Selezione (1-5, default=3): ").strip()
    return MODELLI_WHISPER.get(scelta, "small")

def trova_ultimo_audio(cartella_audio):
    files = [f for f in os.listdir(cartella_audio) if f.lower().endswith(".wav")]
    if not files:
        return None
    files.sort(key=lambda f: os.path.getmtime(os.path.join(cartella_audio, f)), reverse=True)
    ultimo = files[0]
    backup_dir = os.path.join(cartella_audio, "Backup")
    os.makedirs(backup_dir, exist_ok=True)

    # Sposta tutti gli altri file in backup (mantieni solo gli ultimi 10)
    for f in files[1:]:
        orig_path = os.path.join(cartella_audio, f)
        dest_name = f
        i = 1
        while os.path.exists(os.path.join(backup_dir, dest_name)):
            base, ext = os.path.splitext(f)
            dest_name = f"{base}_{i}{ext}"
            i += 1
        shutil.move(orig_path, os.path.join(backup_dir, dest_name))
        print(Fore.YELLOW + f"[INFO] File spostato in backup: {dest_name}" + Style.RESET_ALL)

    # Mantieni solo gli ultimi 10 in backup
    backup_files = sorted(os.listdir(backup_dir), key=lambda f: os.path.getmtime(os.path.join(backup_dir, f)), reverse=True)
    for old_file in backup_files[10:]:
        os.remove(os.path.join(backup_dir, old_file))
        # Se vuoi, puoi aggiungere qui un print giallo anche per eliminazioni, altrimenti lascialo silenzioso

    return os.path.join(cartella_audio, ultimo)


def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def trascrivi_sottotitoli(audio_file, modello):
    cartella_sottotitoli = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Sottotitoli"))
    os.makedirs(cartella_sottotitoli, exist_ok=True)
    srt_output = os.path.join(cartella_sottotitoli, "sottotitoli.srt")
    srt_lavoro = os.path.join(cartella_sottotitoli, "sottotitoli_lavoro.srt")

    if not os.path.isfile(audio_file):
        print(Fore.RED + f"[ERRORE] File audio non trovato: {audio_file}" + Style.RESET_ALL)
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Carico modello Whisper ({modello}) su {device.upper()}")
    model = whisper.load_model(modello).to(device)

    print(f"[INFO] Trascrivo l'audio: {audio_file}")
    try:
        result = model.transcribe(
            audio_file,
            language='en',
            task='transcribe',
            verbose=False,
            condition_on_previous_text=False,
            fp16=False
        )
    except Exception as e:
        print(Fore.RED + f"[ERRORE] Trascrizione fallita: {e}" + Style.RESET_ALL)
        return

    segments = result['segments']
    n = len(segments)
    nuova_lista = []

    for i, seg in enumerate(segments):
        start = seg['start']
        text = seg['text'].strip()

        parole = len(text.split())
        durata_stim = max(parole * 0.35, 0.5)

        # Calcolo fine frase con buffer definito da variabile BUFFER_POST_FRASE
        if i < n-1:
            start_next = segments[i+1]['start']
            fine = min(start + durata_stim + BUFFER_POST_FRASE, start_next)
        else:
            fine = start + durata_stim + BUFFER_POST_FRASE

        nuova_lista.append({'start': start, 'end': fine, 'text': text})

    with open(srt_output, 'w', encoding='utf-8') as f:
        for idx, seg in enumerate(nuova_lista, start=1):
            f.write(f"{idx}\n{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}\n{seg['text']}\n\n")

    shutil.copy2(srt_output, srt_lavoro)
    print(Fore.GREEN + f"[OK] Sottotitoli salvati in: {srt_output}" + Style.RESET_ALL)
    print(Fore.GREEN + f"[OK] Copia lavoro creata in: {srt_lavoro}" + Style.RESET_ALL)


def main():
    cartella_audio = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Sottotitoli", "AudioDaSottotitolare"))
    audio_file = trova_ultimo_audio(cartella_audio)
    if not audio_file:
        print(Fore.YELLOW + "[INFO] Nessun file audio trovato nella cartella AudioDaSottotitolare." + Style.RESET_ALL)
        return

    modello = scegli_modello()
    trascrivi_sottotitoli(audio_file, modello)

if __name__ == "__main__":
    main()

# =========================================================
# tts_merge.py
# =========================================================
# Modulo standalone per concatenare file audio TTS
# Input obbligatori: input_dir, output_file, output_format
# =========================================================

import os
from pathlib import Path
from pydub import AudioSegment

def merge_audio_files(input_dir, output_file, output_format="wav"):
    """
    Concatena tutti i file audio in input_dir in un unico file output_file.
    """
    input_dir = Path(input_dir)
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Cartella input non trovata: {input_dir}")

    # Lista file ordinata alfabeticamente
    audio_files = sorted(input_dir.glob("*." + output_format.lower()))
    if not audio_files:
        raise ValueError(f"Nessun file {output_format} trovato in {input_dir}")

    # Primo file come base
    combined = AudioSegment.from_file(audio_files[0], format=output_format)
    
    for audio_file in audio_files[1:]:
        segment = AudioSegment.from_file(audio_file, format=output_format)
        combined += segment

    combined.export(output_file, format=output_format)
    print(f"[TTS Merge] File concatenato creato: {output_file}")

# =========================================================
# BLOCCO 5 – Main standalone CLI
# =========================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Modulo standalone TTS Merge")
    parser.add_argument("--input_dir", required=True, help="Cartella contenente file audio da unire")
    parser.add_argument("--output_file", required=True, help="Percorso file audio di output")
    parser.add_argument("--format", required=True, choices=["wav", "mp3"], help="Formato audio di output")

    args = parser.parse_args()

    merge_audio_files(args.input_dir, args.output_file, args.format.lower())
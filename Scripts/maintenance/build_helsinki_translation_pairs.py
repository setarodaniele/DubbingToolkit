# ==========================================================
# build_helsinki_languages.py
# ----------------------------------------------------------
# Generates:
# - locale/helsinki_languages.json
# - locale/helsinki_languages_complete.json
#
# Used for Helsinki-NLP translation pair verification.
# NOTE:
# This script currently supports ONLY Helsinki models.
# Future migration to multi-model system is planned.
# ==========================================================

import json
import time
import os
from huggingface_hub import repo_exists

# --- Percorsi ---
whisper_file = r"D:\RecordingStudio\DubbingToolkit\locale\whisper_languages.json"
helenski_file = r"D:\RecordingStudio\DubbingToolkit\locale\helenski_languages.json"
helenski_complete_file = r"D:\RecordingStudio\DubbingToolkit\locale\helenski_languages_complete.json"
hf_config_file = r"D:\RecordingStudio\DubbingToolkit\Tools\HuggingFace.json"

# --- Legge il token HuggingFace ---
with open(hf_config_file, "r", encoding="utf-8") as f:
    hf_config = json.load(f)
HF_TOKEN = hf_config["api_key"]

# --- Legge lingue Whisper ---
with open(whisper_file, "r", encoding="utf-8") as f:
    whisper_langs = json.load(f)  # struttura: {"en": "English", "it": "Italian", ...}

codes = list(whisper_langs.keys())

# --- Legge i file esistenti per ripresa ---
helenski_supported = {}
helenski_complete = {}

if os.path.exists(helenski_file):
    with open(helenski_file, "r", encoding="utf-8") as f:
        helenski_supported = json.load(f)
    # converti tutte le liste in set per eliminare duplicati
    for k, v in helenski_supported.items():
        helenski_supported[k] = set(v)

if os.path.exists(helenski_complete_file):
    with open(helenski_complete_file, "r", encoding="utf-8") as f:
        helenski_complete = json.load(f)
else:
    # inizializza il complete file con tutte le lingue e tutte le destinazioni "unknown"
    for src in codes:
        helenski_complete[src] = {tgt: "unknown" for tgt in codes if tgt != src}

# --- Verifica incrociata con Helsinki-NLP ---
for src in codes:
    existing = helenski_complete.get(src, {})
    all_dest = set(codes) - {src}
    if all(existing.get(tgt) in ("true", "false") for tgt in all_dest):
        print(f"--- Lingua sorgente {src} già completa, salto ---")
        continue

    helenski_supported.setdefault(src, set())
    helenski_complete.setdefault(src, {tgt: "unknown" for tgt in all_dest})
    print(f"--- Lingua sorgente: {src} ---")

    for tgt in codes:
        if src == tgt or helenski_complete[src].get(tgt) in ("true", "false"):
            continue

        repo = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
        try:
            if repo_exists(repo, token=HF_TOKEN):
                helenski_supported[src].add(tgt)
                helenski_complete[src][tgt] = "true"
                print(f"  → {src} → {tgt} : OK")
            else:
                helenski_complete[src][tgt] = "false"
                print(f"  → {src} → {tgt} : NO")
        except Exception as e:
            print(f"  → {src} → {tgt} : ERRORE ({e})")

        time.sleep(0.3)

    # --- Salva subito dopo ogni lingua ---
    with open(helenski_file, "w", encoding="utf-8") as f:
        f.write("{\n")
        for i, (key, tgts) in enumerate(helenski_supported.items()):
            tgts_sorted = sorted(tgts)
            tgts_str = ", ".join(f'"{t}"' for t in tgts_sorted)
            line = f'  "{key}": [{tgts_str}]'
            if i < len(helenski_supported) - 1:
                line += ","
            line += "\n"
            f.write(line)
        f.write("}\n")

    with open(helenski_complete_file, "w", encoding="utf-8") as f:
        json.dump(helenski_complete, f, ensure_ascii=False, indent=2)


print(f"\nLista Helsinki-NLP salvata in: {helenski_file}")
print(f"File completo di controllo salvato in: {helenski_complete_file}")

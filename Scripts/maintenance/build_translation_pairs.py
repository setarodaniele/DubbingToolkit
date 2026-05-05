# build_translation_pairs.py
# Script to build and update translation pairs for all source->target languages
# Checks multiple models per language pair using HuggingFace API and updates JSON files incrementally

import json
import os
import time
from huggingface_hub import repo_exists
from pathlib import Path

# --------------------------
# 1. Paths
# --------------------------
# Base del progetto
BASE_DIR = Path(__file__).resolve().parent.parent  # sale da Scripts/maintenance a DubbingToolkit
# --------------------------
# File letti
# --------------------------
whisper_file = BASE_DIR / "locale" / "whisper_languages.json"
hf_config_file = BASE_DIR / "Tools" / "HuggingFace.json"
# --------------------------
# File generati / salvati
# --------------------------
supported_languages_file = BASE_DIR / "locale" / "supported_languages.json"
translation_models_complete_file = BASE_DIR / "locale" / "translation_models_complete.json"

# --------------------------
# 2. Models to check
# --------------------------
models_list = [
    # Modelli a coppia di lingue
    "Helsinki-NLP/opus-mt-{src}-{tgt}",          # modello specifico per coppia
    "Xenova/opus-mt-{src}-{tgt}",                # modello specifico per coppia
    "Nextcloud-AI/opus-mt-{src}-{tgt}",         # modello specifico per coppia
    #"Infomaniak-AI/onnx-opus-mt-{src}-{tgt}",   # modello specifico per coppia ONNX
    "onnx-community/opus-mt-{src}-{tgt}",       # modello specifico per coppia ONNX
    "manancode/opus-mt-{src}-{tgt}-ctranslate2-android",  # modello specifico per coppia Android/ONNX
  
    # Modelli multilingua (supportano molte lingue in un unico modello)
    #"Xenova/m2m100_418M",                        # multilingua, 418M parametri
    #"facebook/nllb-200-distilled-600M",         # multilingua, molte lingue (distilled)
    #"google/madlad400-3b-mt"                     # multilingua, molto grande, più lingue  
]

# --------------------------
# 3. Load HuggingFace token
# --------------------------
with open(hf_config_file, "r", encoding="utf-8") as f:
    hf_config = json.load(f)
HF_TOKEN = hf_config["api_key"]

# --------------------------
# 4. Load Whisper languages
# --------------------------
with open(whisper_file, "r", encoding="utf-8") as f:
    whisper_langs = json.load(f)

codes = sorted(list(whisper_langs.keys()))

# --------------------------
# 5. Load or initialize language files
# --------------------------
supported_languages = {}
translation_models_complete = {}

if os.path.exists(supported_languages_file):
    with open(supported_languages_file, "r", encoding="utf-8") as f:
        supported_languages = json.load(f)
    for k, v in supported_languages.items():
        supported_languages[k] = set(v)

if os.path.exists(translation_models_complete_file):
    with open(translation_models_complete_file, "r", encoding="utf-8") as f:
        translation_models_complete = json.load(f)

# ==========================================================
# 6. Structural alignment (add/remove languages and models)
# ==========================================================

structure_modified = False

# --------------------------
# 6.1 Remove obsolete languages and models
# --------------------------
for src in list(translation_models_complete.keys()):
    if src not in codes:
        del translation_models_complete[src]
        structure_modified = True
        continue

    for tgt in list(translation_models_complete[src].keys()):
        if tgt not in codes or tgt == src:
            del translation_models_complete[src][tgt]
            structure_modified = True
            continue

        for model in list(translation_models_complete[src][tgt].keys()):
            if not any(m.format(src=src, tgt=tgt) == model for m in models_list):
                del translation_models_complete[src][tgt][model]
                structure_modified = True

# --------------------------
# 6.2 Add missing languages and models
# --------------------------
for src in codes:
    translation_models_complete.setdefault(src, {})

    for tgt in codes:
        if src == tgt:
            continue

        translation_models_complete[src].setdefault(tgt, {})

        for model_template in models_list:
            model_name = model_template.format(src=src, tgt=tgt)

            if model_name not in translation_models_complete[src][tgt]:
                translation_models_complete[src][tgt][model_name] = "unknown"
                structure_modified = True

# --------------------------
# 6.3 Rebuild supported_languages from scratch
# --------------------------
supported_languages = {}

for src, targets in translation_models_complete.items():
    supported_languages[src] = set()

    for tgt, models in targets.items():
        if any(status == "true" for status in models.values()):
            supported_languages[src].add(tgt)

# ==========================================================
# 7. Verify model existence online (with per-language save)
# ==========================================================

for src in codes:
    print(f"\n--- Lingua sorgente: {src} ---")
    modified = False  # track changes for this language

    for tgt in codes:
        if src == tgt:
            continue

        for model_template in models_list:
            model_name = model_template.format(src=src, tgt=tgt)
            status = translation_models_complete[src][tgt].get(model_name, "unknown")

            if status in ("true", "false", "error"):
                continue  # skip already verified

            try:
                exists = repo_exists(model_name, token=HF_TOKEN)
                translation_models_complete[src][tgt][model_name] = "true" if exists else "false"

                if exists:
                    # Add target to supported_languages[src], will be rebuilt below anyway
                    pass

                print(f"  → {src} → {tgt} | {model_name} : {translation_models_complete[src][tgt][model_name]}")
                modified = True

            except Exception as e:
                translation_models_complete[src][tgt][model_name] = "error"
                print(f"  → {src} → {tgt} | {model_name} : ERROR ({e})")
                modified = True

            time.sleep(0.3)

    # --------------------------
    # 7.1 Rebuild supported_languages from scratch
    # --------------------------
    supported_languages = {}
    for s, targets in translation_models_complete.items():
        supported_languages[s] = set()
        for t, models in targets.items():
            if any(status == "true" for status in models.values()):
                supported_languages[s].add(t)

    # --------------------------
    # 7.2 Save supported_languages.json
    # --------------------------
    with open(supported_languages_file, "w", encoding="utf-8") as f:
        f.write("{\n")
        items = sorted(supported_languages.items())
        for i, (key, tgts) in enumerate(items):
            tgts_sorted = sorted(list(tgts))
            tgts_str = ", ".join(f'"{t}"' for t in tgts_sorted)
            line = f'  "{key}": [{tgts_str}]'
            if i < len(items) - 1:
                line += ","
            line += "\n"
            f.write(line)
        f.write("}\n")

    # --------------------------
    # 7.3 Save translation_models_complete.json
    # --------------------------
    with open(translation_models_complete_file, "w", encoding="utf-8") as f:
        f.write("{\n")
        src_items = sorted(translation_models_complete.items())
        for i, (src_key, targets) in enumerate(src_items):
            f.write(f'  "{src_key}": {{\n')
            tgt_items = sorted(targets.items())
            for j, (tgt_key, models) in enumerate(tgt_items):
                models_str = ", ".join(f'"{model}":"{status}"' for model, status in models.items())
                line = f'    "{tgt_key}": {{{models_str}}}'
                if j < len(tgt_items) - 1:
                    line += ","
                f.write(line + "\n")
            f.write("  }")
            if i < len(src_items) - 1:
                f.write(",")
            f.write("\n")
        f.write("}\n")

    print(f"\nLingua {src} verificata e file salvati.\n")


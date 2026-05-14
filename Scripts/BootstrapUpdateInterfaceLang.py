#BootstrapUpdateInterfaceLang.py
import json
import sys
from pathlib import Path
import shutil

settings_path = Path(sys.argv[1])
default_path = Path(sys.argv[2])
new_lang = sys.argv[3]

# Se il file settings.json non esiste, crealo dai default
if not settings_path.exists():
    shutil.copyfile(default_path, settings_path)

# Carica
with settings_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

# Aggiorna solo la lingua
data["interface_lang"] = new_lang

# Salva con formattazione stabile
with settings_path.open("w", encoding="utf-8", newline="\n") as f:
    json.dump(
        data,
        f,
        indent=2,
        ensure_ascii=False
    )
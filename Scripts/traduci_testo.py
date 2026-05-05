# traduci_testo.py

# ==========================
# 1.0 Imports
# ==========================
from pathlib import Path
from colorama import init, Fore, Style
import torch
from transformers import MarianMTModel, MarianTokenizer
import json
from info_manager import InfoManager
from datetime import datetime
import json
from pathlib import Path

from core.ui_printer import print_infobox, print_menu, print_input, print_error, print_success, print_menu_header
from core.ui_colors import COLOR_SUCCESS, COLOR_ERROR
from core.file_selector import select_input_file, select_input_folder, select_output_folder
from core.messages import Messages
from core.logger import logger
from menu_lingue import seleziona_lingua
from backup_utils import manage_history
import traceback as _tb_module

# Initialize Colorama
init(autoreset=True)


# ==========================
# 2.0 Paths and constants
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_FILE = BASE_DIR / "Settings" / "settings.json"
TRANSCRIPTS_DIR = BASE_DIR / "Transcripts"
TRANSLATED_DIR = BASE_DIR / "Translated"

# Placeholder for Helsinki languages file
#OLD_HELSINKI_LANG_FILE = BASE_DIR / "locale/supported_languages.json"
HELSINKI_LANG_FILE = BASE_DIR / "locale/helsinki_languages.json"

# ==========================
# 2.1 Load settings and localization
# ==========================
import json

def load_settings():
    if not SETTINGS_FILE.exists():
        raise FileNotFoundError(f"Settings file not found: {SETTINGS_FILE}")
    with open(SETTINGS_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)

# Load user settings
settings = load_settings()

# Load interface localization
# Messages class centralizes localization:
# - Reads interface language from settings.json ("interface_lang")
# - Loads corresponding JSON from locale/Active (e.g., it.json)
# - Provides fallback handling for missing keys
# - All scripts should use this single instance for message strings
messages = Messages(settings_file=SETTINGS_FILE)

# Load supported languages
with open(HELSINKI_LANG_FILE, "r", encoding="utf-8-sig") as f:
    supported_languages = json.load(f)

# ==========================
# 3.0 Transcript utilities
# ==========================
def get_latest_transcript_folder():
    if not TRANSCRIPTS_DIR.exists():
        return None
    folders = [f for f in TRANSCRIPTS_DIR.iterdir() if f.is_dir()]
    if not folders:
        return None
    folders.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return folders[0]

def get_srt_files_from_folder(folder: Path):
    return sorted(f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == ".srt" and not f.name.endswith("_info.txt"))

def get_work_srt_from_folder(folder: Path):
    return [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == ".srt" and f.name.endswith("_work.srt")]

# ==========================
# 3.1 File selection helpers
# ==========================
def seleziona_file_srt(messages, base_folder: Path):
    """
    File selection with folders or manual dialog.
    """
    folders = [f for f in base_folder.iterdir() if f.is_dir()]
    folders.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    while True:        
        print("\n" + messages.FILE_SELECTOR_dialog_title_input_folder)
        for i, folder in enumerate(folders, start=1):
            print(f"{i}. [DIR] {folder.name}")
        manual_index = len(folders) + 1
        print(f"{manual_index}. {messages.FILE_SELECTOR_option_select_manual}")
        print("0. " + messages.FILE_SELECTOR_selection_cancelled)

        choice = input(messages.FILE_SELECTOR_prompt_choice + " ").strip()
        if not choice.isdigit():
            print_error(messages.FILE_SELECTOR_invalid_choice)
            continue
        choice = int(choice)

        if choice == 0:
            return None
        elif 1 <= choice <= len(folders):
            selected_folder = folders[choice - 1]
            srt_files = get_work_srt_from_folder(selected_folder)
            
            # --- Informational message about filtered files ---
            print()
            print(Fore.YELLOW + messages.TRANSLATE_only_work_srt_note + Style.RESET_ALL)
            if not srt_files:
                print_error(messages.TRANSLATE_no_work_srt_in_latest_folder)
                continue
            for j, f in enumerate(srt_files, start=1):
                print(f"{j}. {f.name}")
            while True:
                file_choice = input(messages.FILE_SELECTOR_prompt_choice + " ").strip()
                if not file_choice.isdigit():
                    print_error(messages.FILE_SELECTOR_invalid_choice)
                    continue
                file_choice = int(file_choice)
                if 1 <= file_choice <= len(srt_files):
                    return srt_files[file_choice - 1]
                elif file_choice == 0:
                    break
                else:
                    print_error(messages.FILE_SELECTOR_invalid_choice)
        elif choice == manual_index:
            return select_input_file(messages, initial_folder=base_folder, file_types=[("SRT files", "*.srt")])
        else:
            print_error(messages.FILE_SELECTOR_invalid_choice)

# ==========================
# 4.0 Translation engine
# ==========================
def traduci_testo(messages, settings):
    """Translate a selected SRT file using MarianMT, handles language confirmation, device, and output folder"""
    _t0 = datetime.now()
    _segments_translated = 0
    logger.info("traduci_testo", "traduci_testo", "Translation started")

    # --- 4.1 LANGUAGE MENU ---
    while True:
        src_lang = settings.get("Translation_Source_Lang")
        tgt_lang = settings.get("Translation_Target_Lang")

        src_name = getattr(messages, f'LANG_{src_lang}', src_lang)
        tgt_name = getattr(messages, f'LANG_{tgt_lang}', tgt_lang)

        compatibile = tgt_lang in supported_languages.get(src_lang, [])

        compat_text = getattr(messages, "TRANSLATE_compat_ok") if compatibile else getattr(messages, "TRANSLATE_compat_not_ok")
        compat_color = COLOR_SUCCESS if compatibile else COLOR_ERROR

        print_infobox(
            lines=[
                getattr(messages, "TRANSLATE_info_box_source").format(lang=src_name),
                getattr(messages, "TRANSLATE_info_box_target").format(lang=tgt_name)
            ],
            status_line=compat_text,
            status_color=compat_color,
            warning=getattr(messages, "TRANSLATE_source_warning")
        )

        print_menu_header(getattr(messages, "MENU_translation_title"))

        options_dict = {
            "1": getattr(messages, "TRANSLATE_option_proceed"),
            "2": getattr(messages, "TRANSLATE_option_change_source"),
            "3": getattr(messages, "TRANSLATE_option_change_target"),
            "0": getattr(messages, "TRANSLATE_option_cancel")
        }
        print_menu(options_dict)
        choice = print_input(messages.TRANSLATE_prompt_choice).strip()

        if choice == "1" or choice == "":
            if not compatibile:
                print_error(
                    getattr(messages, "TRANSLATE_lang_not_supported")
                    .format(src=src_name, tgt=tgt_name)
                )
                continue
            break  # proceed
        elif choice == "2":
            nuova_src = seleziona_lingua(messages, settings, context="translation_source", default=src_lang)
            if nuova_src:
                src_lang = nuova_src
            continue
        elif choice == "3":
            nuova_tgt = seleziona_lingua(messages, settings, context="translation_target", default=tgt_lang)
            if nuova_tgt:
                tgt_lang = nuova_tgt
            continue
        elif choice == "0":
            return  # cancel
        else:
            print_error(getattr(messages, "TRANSLATE_invalid_choice"))
            continue

    # --- 4.2 File selection ---
    selected_srt = seleziona_file_srt(messages, TRANSCRIPTS_DIR)
    if not selected_srt:
        return

    # --- 4.3 Device selection ---
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(Fore.YELLOW + getattr(messages, "TRANSLATE_using_device").format(device=device.upper()) + Style.RESET_ALL)


    # --- 4.5 HELSINKI ONLY MODEL LOADER ---
    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
    try:
        print(Fore.CYAN + "[INFO] " + getattr(messages, "TRANSLATE_loading_model").format(model=model_name) + Style.RESET_ALL)
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name).to(device)
    except Exception as e:
        print_error(getattr(messages, "TRANSLATE_model_load_failed").format(model=model_name))
        logger.error("traduci_testo", "traduci_testo",
                     f"Model load failed: {model_name} — {e}",
                     error_code="TRANSLATION_MODEL_LOAD_FAILED", error_category="SYSTEM",
                     is_retryable=True,
                     context={"model": model_name, "src_lang": src_lang, "tgt_lang": tgt_lang},
                     traceback=_tb_module.format_exc())
        return

    # --- 4.6 Output folder & translation ---
    timestamp_tag = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_folder = TRANSLATED_DIR / f"{timestamp_tag}_{tgt_lang}_{selected_srt.parent.name}_{src_lang}"
    output_folder.mkdir(parents=True, exist_ok=True)
    output_srt = output_folder / f"{selected_srt.stem}_{tgt_lang}.srt"

    with open(selected_srt, "r", encoding="utf-8") as f:
        lines = f.readlines()

    translated_lines = []
    buffer = []

    def translate_block(block):
        if not block:
            return []
        batch = tokenizer(block, return_tensors="pt", padding=True, truncation=True).to(device)
        translated = model.generate(**batch)
        return tokenizer.batch_decode(translated, skip_special_tokens=True)

    for line in lines:
        stripped = line.strip()
        if stripped.isdigit() or "-->" in stripped or stripped == "":
            if buffer:
                translated_lines.extend([t + "\n" for t in translate_block(buffer)])
                _segments_translated += 1
                buffer = []
            translated_lines.append(line)
        else:
            buffer.append(stripped)
    if buffer:
        translated_lines.extend([t + "\n" for t in translate_block(buffer)])
        _segments_translated += 1

    with open(output_srt, "w", encoding="utf-8") as f:
        f.writelines(translated_lines)

    print(Fore.CYAN + getattr(messages, "TRANSLATE_completed").format(file=output_srt) + Style.RESET_ALL)

    # --- 4.7 Update history ---
    manage_history(TRANSLATED_DIR, settings, messages)

    # ==========================
    # 4.8 Update project JSON and info.txt
    # ==========================
    info_manager = InfoManager(
        base_dir=output_folder,
        current_section="traduzioni",
        source_json=selected_srt.parent / "project_info.json"
    )

    info_manager.update_traduzione(
        source_file=selected_srt,
        target_file=output_srt,
        source_lang=src_lang,
        target_lang=tgt_lang,
        translation_model=model_name,
        messages=messages
    )

    _dur = round((datetime.now() - _t0).total_seconds() * 1000)
    logger.operation("traduci_testo", "traduci_testo", "Translation completed",
                     status="SUCCESS", duration_ms=_dur,
                     context={"provider": "Helsinki-NLP/MarianMT",
                              "model": model_name,
                              "src_lang": src_lang, "tgt_lang": tgt_lang,
                              "segments_translated": _segments_translated,
                              "output_file": output_srt.name})
    
# ==========================
# 5.0 Entry point
# ==========================
if __name__ == "__main__":
    traduci_testo(messages, settings)

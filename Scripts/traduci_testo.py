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

from core.ui_printer import print_infobox, print_menu, print_input, print_error, print_success, print_menu_header, offer_open_folder
from core.ui_colors import COLOR_SUCCESS, COLOR_ERROR
from core.file_selector import select_input_file, select_input_folder, select_output_folder
from core.messages import Messages
from core.logger import logger
from menu_lingue import seleziona_lingua
import traceback as _tb_module
from core.workspace_manager import WorkspaceManager
from core.utils_settings import write_json_atomic
from core.archive_pruner import prune_with_confirmation, prune_by_language

# Initialize Colorama
init(autoreset=True)


# ==========================
# 2.0 Paths and constants
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_FILE = BASE_DIR / "Settings" / "settings.json"
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
# 3.1 File selection helpers
# ==========================
def _collect_work_srts(transcripts_dir):
    """Return list of (track_id, Path) for *_work.srt files in transcripts stage."""
    tracks = []
    if not transcripts_dir.exists():
        return tracks
    for track_dir in sorted(transcripts_dir.iterdir()):
        if not (track_dir.is_dir() and track_dir.name.startswith("track_")):
            continue
        current = track_dir / "current"
        if not current.exists():
            continue
        work_srts = sorted(current.glob("*_work.srt"))
        if work_srts:
            tracks.append((track_dir.name, work_srts[0]))
    return tracks


def seleziona_file_srt(messages, ws):
    """Select a work SRT file from the workspace transcripts stage.

    Returns (track_id, Path) or None if the user cancels.
    """
    transcripts_dir = ws.root / "transcripts"

    while True:
        tracks = _collect_work_srts(transcripts_dir)

        print()
        print(Fore.CYAN + "-" * 28 + Style.RESET_ALL)
        print(Fore.CYAN + messages.TRANSLATE_menu_select_title + Style.RESET_ALL)
        print(Fore.CYAN + "-" * 28 + Style.RESET_ALL)

        if tracks:
            print(f"  1. {messages.TRANSLATE_option_transcripts}")
        else:
            print(Style.DIM + f"  1. {messages.TRANSLATE_option_transcripts}  {messages.MENU_folder_empty}" + Style.RESET_ALL)
        print(f"  2. {messages.FILE_SELECTOR_option_select_manual}")
        print(f"  0. {messages.FILE_SELECTOR_selection_cancelled}")

        choice = input(messages.FILE_SELECTOR_prompt_choice + " ").strip()

        if choice == "0":
            return None
        elif choice == "1":
            if not tracks:
                print(Fore.YELLOW + f"{messages.TRANSLATE_option_transcripts}: {messages.MENU_folder_empty}" + Style.RESET_ALL)
                continue
            # Sub-menu: list work SRT files
            while True:
                print()
                print(Fore.CYAN + "-" * 28 + Style.RESET_ALL)
                print(Fore.CYAN + messages.TRANSLATE_submenu_transcripts + Style.RESET_ALL)
                print(Fore.CYAN + "-" * 28 + Style.RESET_ALL)
                print(Fore.YELLOW + messages.TRANSLATE_only_work_srt_note + Style.RESET_ALL)
                for i, (track_id, fpath) in enumerate(tracks, 1):
                    print(f"  {i}. [{track_id}] {fpath.name}")
                print(f"  0. {messages.MENU_option_back}")
                sub = input(messages.FILE_SELECTOR_prompt_choice + " ").strip()
                if not sub.isdigit():
                    print_error(messages.FILE_SELECTOR_invalid_choice)
                    continue
                sub = int(sub)
                if sub == 0:
                    break  # back to main menu
                elif 1 <= sub <= len(tracks):
                    track_id, fpath = tracks[sub - 1]
                    return (track_id, fpath)
                else:
                    print_error(messages.FILE_SELECTOR_invalid_choice)
        elif choice == "2":
            result = select_input_file(messages, initial_folder=transcripts_dir,
                                       file_types=[("SRT files", "*.srt")])
            if result:
                parts = Path(result).parts
                try:
                    idx = next(i for i, p in enumerate(parts) if p == "transcripts")
                    tid = parts[idx + 1] if parts[idx + 1].startswith("track_") else None
                except (StopIteration, IndexError):
                    tid = None
                if tid is None:
                    translated_dir = ws.root / "translated"
                    existing = sorted(
                        d.name for d in translated_dir.iterdir()
                        if d.is_dir() and d.name.startswith("track_")
                    ) if translated_dir.exists() else []
                    try:
                        n = int(existing[-1].split("_")[1]) + 1 if existing else 1
                    except (IndexError, ValueError):
                        n = len(existing) + 1
                    tid = f"track_{n:02d}"
                return (tid, Path(result))
            # dialog closed without selection — loop back to menu
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

    # --- 4.2 Resolve workspace ---
    ws = WorkspaceManager.get_active()

    # --- 4.3 File selection ---
    selection = seleziona_file_srt(messages, ws)
    if not selection:
        return
    track_id, selected_srt = selection

    # --- 4.4 Device selection ---
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

    # --- 4.5 Output folder & translation ---
    ws.rotate_to_archive("translated", track_id)
    prune_with_confirmation(
        ws, "translated", track_id, messages,
        show_confirmations=settings.get("show_confirmations", True),
        use_trash=settings.get("use_trash", False),
        max_count=settings.get("max_backups", 10),
    )
    prune_by_language(
        ws, "translated", track_id,
        lang_key="target_lang",
        max_per_lang=settings.get("max_backups_per_language", 10),
        use_trash=settings.get("use_trash", False),
    )
    output_folder = ws.stage_current("translated", track_id)
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

    # --- 4.6 Write per-track metadata ---
    _created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_json_atomic(output_folder / "metadata.json", {
        "schema_version":    1,
        "track_id":          track_id,
        "created_at":        _created_at,
        "source_srt":        selected_srt.name,
        "output_srt":        output_srt.name,
        "source_lang":       src_lang,
        "target_lang":       tgt_lang,
        "translation_model": model_name,
        "segments_translated": _segments_translated,
    })

    try:
        InfoManager(ws.root).update_traduzione(track_id, {
            "created_at":        _created_at,
            "translation_model": model_name,
            "source_lang":       src_lang,
            "target_lang":       tgt_lang,
            "segments_translated": _segments_translated,
        })
    except Exception:
        pass

    _dur = round((datetime.now() - _t0).total_seconds() * 1000)
    logger.operation("traduci_testo", "traduci_testo", "Translation completed",
                     status="SUCCESS", duration_ms=_dur,
                     context={"provider": "Helsinki-NLP/MarianMT",
                              "model": model_name,
                              "src_lang": src_lang, "tgt_lang": tgt_lang,
                              "segments_translated": _segments_translated,
                              "output_file": output_srt.name,
                              "workspace": ws.name})

    offer_open_folder(output_folder, messages)
    
# ==========================
# 5.0 Entry point
# ==========================
if __name__ == "__main__":
    traduci_testo(messages, settings)

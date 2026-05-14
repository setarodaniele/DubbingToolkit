# =========================================================
# settings_manager.py
# DubbingToolkit Settings Manager
# =========================================================

from pathlib import Path
from colorama import Fore, Style
import json
import subprocess
import os
from core.messages import Messages
from core.input_parsing import parse_int, parse_float, parse_yes_no, is_yes
from core.utils_settings import write_json_atomic, merge_and_rebuild, PERSISTENT_FIELDS

_SETTINGS_FILE          = Path.cwd() / "Settings" / "settings.json"
_DEFAULT_FILE           = Path.cwd() / "Settings" / "settings_default.json"
_PERSISTENT_FILE        = Path.cwd() / "Settings" / "settings_persistent.json"
_PERSISTENT_DEFAULT     = Path.cwd() / "Settings" / "settings_persistent_default.json"


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def _save_persistent_and_rebuild(persistent: dict) -> None:
    write_json_atomic(_PERSISTENT_FILE, persistent)
    merge_and_rebuild(_DEFAULT_FILE, _PERSISTENT_FILE, _SETTINGS_FILE)



def main(messages):
    while True:
        print()
        print(Fore.CYAN + "-"*30)
        print(messages.SETTINGS_MENU_TITLE)
        print("-"*30 + Style.RESET_ALL)

        print(f"1) {messages.SETTINGS_MODIFY}")
        print(f"2) {messages.SETTINGS_SOFT_RESET}")
        print(f"3) {messages.SETTINGS_MODIFY_LANGUAGE}")
        print(f"9) {messages.SETTINGS_HARD_RESET}")
        print(f"0) {messages.SETTINGS_BACK}")

        choice = input(messages.SETTINGS_PROMPT + " ").strip()

        if choice == "1":
            if modify_settings(messages) == "back_to_main":
                break
        elif choice == "2":
            if default_setting(messages) == "back_to_main":
                break
        elif choice == "3":
            updated_messages = modify_language(messages)
            if isinstance(updated_messages, Messages):
                messages = updated_messages
        elif choice == "9":
            if hard_reset(messages) == "back_to_main":
                break
        elif choice == "0":
            print(Fore.CYAN + messages.SETTINGS_BACK_TO_MENU + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + messages.SETTINGS_INVALID_CHOICE + Style.RESET_ALL)
            
    return messages


def modify_settings(messages):
    settings = _load(_SETTINGS_FILE)

    # ===============================
    # DISPLAY CURRENT SETTINGS
    # ===============================
    print()
    print(Fore.YELLOW + messages.SETTINGS_CURRENT_SETTINGS_TITLE + Style.RESET_ALL)
    print(f"1) {messages.SETTINGS_ASK_MAX_BACKUPS}: {settings.get('max_backups', 10)}")
    print(f"2) {messages.SETTINGS_ASK_MAX_BACKUPS_LANG}: {settings.get('max_backups_per_language', 10)}")
    print(f"3) {messages.SETTINGS_ASK_MAX_FOLDER_SIZE_GB}: {settings.get('max_folders_size_gb', 5)}")
    print(f"4) {messages.SETTINGS_ASK_SHOW_CONFIRMATIONS}: {messages.GENERAL_YES if settings.get('show_confirmations', True) else messages.GENERAL_NO}")
    print(f"5) {messages.SETTINGS_ASK_USE_TRASH}: {messages.GENERAL_YES if settings.get('use_trash', False) else messages.GENERAL_NO}")

    # ===============================
    # MODIFY SETTINGS HEADER
    # ===============================
    print()
    print(Fore.YELLOW + messages.SETTINGS_MODIFY_SETTINGS_TITLE + Style.RESET_ALL)
    print(Fore.YELLOW + "-" * 40 + Style.RESET_ALL)

    # -------------------------------
    # 1) Maximum total backups (int > 0)
    # -------------------------------
    current = settings.get('max_backups', 10)
    while True:
        raw = input(Fore.YELLOW + f"{messages.SETTINGS_ASK_MAX_BACKUPS} [{current}]: " + Style.RESET_ALL).strip()
        if raw == "":
            break
        try:
            value = parse_int(raw)
            if value > 0:
                settings['max_backups'] = value
                break
        except ValueError:
            pass
        print(Fore.RED + messages.SETTINGS_INVALID_VALUE + Style.RESET_ALL)

    # -------------------------------
    # 2) Maximum backups per language (int > 0)
    # -------------------------------
    current = settings.get('max_backups_per_language', 10)
    while True:
        raw = input(Fore.YELLOW + f"{messages.SETTINGS_ASK_MAX_BACKUPS_LANG} [{current}]: " + Style.RESET_ALL).strip()
        if raw == "":
            break
        try:
            value = parse_int(raw)
            if value > 0:
                settings['max_backups_per_language'] = value
                break
        except ValueError:
            pass
        print(Fore.RED + messages.SETTINGS_INVALID_VALUE + Style.RESET_ALL)

    # -------------------------------
    # 3) Maximum folder size in GB (float > 0, comma or dot)
    # -------------------------------
    current = settings.get('max_folders_size_gb', 5)
    while True:
        raw = input(Fore.YELLOW + f"{messages.SETTINGS_ASK_MAX_FOLDER_SIZE_GB} [{current}]: " + Style.RESET_ALL).strip()
        if raw == "":
            break
        try:
            value = parse_float(raw)
            if value > 0:
                settings['max_folders_size_gb'] = value
                break
        except ValueError:
            pass
        print(Fore.RED + messages.SETTINGS_INVALID_VALUE + Style.RESET_ALL)

    # -------------------------------
    # 4) Show confirmations (Yes/No)
    # -------------------------------
    current = settings.get('show_confirmations', True)
    current_label = messages.GENERAL_YES if current else messages.GENERAL_NO
    while True:
        raw = input(Fore.YELLOW + f"{messages.SETTINGS_ASK_SHOW_CONFIRMATIONS} [{messages.GENERAL_YES}/{messages.GENERAL_NO}] ({current_label}): " + Style.RESET_ALL).strip().lower()
        if raw == "":
            break
        try:
            settings['show_confirmations'] = parse_yes_no(raw)
            break
        except ValueError:
            print(Fore.RED + messages.SETTINGS_INVALID_VALUE + Style.RESET_ALL)

    # -------------------------------
    # 5) Use trash for backup deletion (Yes/No)
    # -------------------------------
    current = settings.get('use_trash', False)
    current_label = messages.GENERAL_YES if current else messages.GENERAL_NO
    while True:
        raw = input(Fore.YELLOW + f"{messages.SETTINGS_ASK_USE_TRASH} [{messages.GENERAL_YES}/{messages.GENERAL_NO}] ({current_label}): " + Style.RESET_ALL).strip().lower()
        if raw == "":
            break
        try:
            settings['use_trash'] = parse_yes_no(raw)
            break
        except ValueError:
            print(Fore.RED + messages.SETTINGS_INVALID_VALUE + Style.RESET_ALL)

    # Save persistent fields → rebuild settings.json
    persistent = _load(_PERSISTENT_FILE) if _PERSISTENT_FILE.exists() else {}
    for key in PERSISTENT_FIELDS:
        if key in settings:
            persistent[key] = settings[key]
    _save_persistent_and_rebuild(persistent)

    print(Fore.GREEN + messages.SETTINGS_MODIFY_CONFIRM + Style.RESET_ALL)
    print(Fore.CYAN + messages.SETTINGS_BACK_TO_MENU + Style.RESET_ALL)
    return "back_to_main"


def modify_language(messages):
    settings = _load(_SETTINGS_FILE)
    # Language folders
    locale_folder = Path.cwd() / "Locale"
    system_folder = locale_folder / "System"
    active_folder = locale_folder / "Active"
    languages_file = system_folder / "languages.json"
    # Load language map from system folder
    with languages_file.open("r", encoding="utf-8-sig") as f:
        languages_map = json.load(f)
    # List all available languages that have an active JSON file
    available_langs = [
        key for key in languages_map.keys()
        if not key.endswith("_comment") and (active_folder / f"{key}.json").exists()
    ]
    # Get current interface language from settings
    current_lang = settings.get("interface_lang", "en")
    print("\n" + Fore.YELLOW + f"{messages.SETTINGS_CURRENT_LANGUAGE}: {languages_map.get(current_lang, current_lang).capitalize()}" + Style.RESET_ALL)
    # Show available languages
    for idx, key in enumerate(available_langs, 1):
        print(f"{idx}) {languages_map[key]}")
    # Prompt user for selection
    raw = input(Fore.YELLOW + f"{messages.SETTINGS_SELECT_LANGUAGE} (press Enter for default: {current_lang}): " + Style.RESET_ALL).strip()
    if raw == "":
        selected_lang = current_lang
    else:
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(available_langs):
                selected_lang = available_langs[idx]
            else:
                print(Fore.RED + messages.SETTINGS_INVALID_CHOICE + Style.RESET_ALL)
                return
        except ValueError:
            print(Fore.RED + messages.SETTINGS_INVALID_CHOICE + Style.RESET_ALL)
            return
    # Save to persistent → rebuild settings.json
    persistent = _load(_PERSISTENT_FILE) if _PERSISTENT_FILE.exists() else {}
    persistent["interface_lang"] = selected_lang
    _save_persistent_and_rebuild(persistent)
    os.environ["SELECTED_LANG"] = selected_lang
    # Create a new Messages object with updated language
    new_messages = Messages()
    readable_lang = languages_map.get(selected_lang, selected_lang).capitalize()
    # Messaggio nella lingua vecchia
    print(Fore.GREEN + messages.SETTINGS_LANGUAGE_UPDATED.format(readable_lang) + Style.RESET_ALL)
    # Messaggio nella lingua nuova
    print(Fore.GREEN + new_messages.SETTINGS_LANGUAGE_UPDATED.format(readable_lang) + Style.RESET_ALL)
    return new_messages




# =========================================================
# SETTINGS LOADING
# =========================================================
def default_setting(messages=None, preserve_interface_lang=False):
    # Soft reset: restore settings_persistent.json from its defaults,
    # then rebuild settings.json via merge.
    import shutil
    shutil.copyfile(_PERSISTENT_DEFAULT, _PERSISTENT_FILE)
    merge_and_rebuild(_DEFAULT_FILE, _PERSISTENT_FILE, _SETTINGS_FILE)
    if messages:
        print(Fore.GREEN + messages.Reset_SoftResetComplete + Style.RESET_ALL)
    return "back_to_main"


def hard_reset(messages):
    confirm1 = input(Fore.YELLOW + messages.Reset_HardConfirm1 + " (Y/N): " + Style.RESET_ALL).strip()
    if not is_yes(confirm1, messages):
        print(Fore.YELLOW + messages.Reset_HardCancelled + Style.RESET_ALL)
        return "back_to_main"

    confirm2 = input(Fore.YELLOW + messages.Reset_HardConfirm2 + " (Y/N): " + Style.RESET_ALL).strip()
    if not is_yes(confirm2, messages):
        print(Fore.YELLOW + messages.Reset_HardCancelled + Style.RESET_ALL)
        return "back_to_main"

    reset_file = Path.cwd() / "Settings" / "reset.json"
    reset_flags = _load(reset_file)
    reset_flags["reset_pending"] = True
    reset_flags["first_launch"]  = True
    write_json_atomic(reset_file, reset_flags)

    reset_script = Path.cwd() / "Scripts" / "reset_env.ps1"
    try:
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(reset_script)],
            check=True
        )
    except subprocess.CalledProcessError:
        print(Fore.RED + messages.Reset_ScriptFailed + Style.RESET_ALL)
        return

    print(Fore.YELLOW + messages.Reset_HardResetComplete + Style.RESET_ALL)
    return "back_to_main"

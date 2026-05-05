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
from core.input_parsing import parse_int, parse_float, parse_yes_no



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
    settings_file = Path.cwd() / "Settings" / "settings.json"

    # Load current settings
    with settings_file.open("r", encoding="utf-8-sig") as f:
        settings = json.load(f)

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

    # -------------------------------
    # SAVE UPDATED SETTINGS
    # -------------------------------
    with settings_file.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    print(Fore.GREEN + messages.SETTINGS_MODIFY_CONFIRM + Style.RESET_ALL)
    print(Fore.CYAN + messages.SETTINGS_BACK_TO_MENU + Style.RESET_ALL)
    return "back_to_main"


def modify_language(messages):
    settings_file = Path.cwd() / "Settings" / "settings.json"
    # Load current settings
    with settings_file.open("r", encoding="utf-8-sig") as f:
        settings = json.load(f)
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
    # Save selected language directly in settings
    settings["interface_lang"] = selected_lang
    with settings_file.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    # Update environment variable for consistency
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
    settings_file = Path.cwd() / "Settings" / "settings.json"
    default_settings_file = Path.cwd() / "Settings" / "settings_default.json"
    with default_settings_file.open("r", encoding="utf-8-sig") as f:
        default_settings = json.load(f)
    if preserve_interface_lang and settings_file.exists():
        with settings_file.open("r", encoding="utf-8-sig") as f:
            current_settings = json.load(f)
        if "interface_lang" in current_settings:
            default_settings["interface_lang"] = current_settings["interface_lang"]
    with settings_file.open("w", encoding="utf-8") as f:
        json.dump(default_settings, f, indent=2, ensure_ascii=False)
    if messages:
        print(Fore.GREEN + messages.Reset_SoftResetComplete + Style.RESET_ALL)
    return "back_to_main"


def hard_reset(messages):
    confirm1 = input(Fore.YELLOW + messages.Reset_HardConfirm1 + " (Y/N): " + Style.RESET_ALL).strip().lower()
    if confirm1 not in ("y", "yes"):
        print(Fore.YELLOW + messages.Reset_HardCancelled + Style.RESET_ALL)
        return "back_to_main"

    confirm2 = input(Fore.YELLOW + messages.Reset_HardConfirm2 + " (Y/N): " + Style.RESET_ALL).strip().lower()
    if confirm2 not in ("y", "yes"):
        print(Fore.YELLOW + messages.Reset_HardCancelled + Style.RESET_ALL)
        return "back_to_main"

    reset_file = Path.cwd() / "Settings" / "reset.json"
    with reset_file.open("r", encoding="utf-8-sig") as f:
        reset_flags = json.load(f)

    reset_flags["reset_pending"] = True
    reset_flags["first_launch"] = True

    with reset_file.open("w", encoding="utf-8") as f:
        json.dump(reset_flags, f, indent=2, ensure_ascii=False)

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

import os
import json
import shutil
from colorama import Fore, Style


def seleziona_lingua(messages, settings=None, context="translation_source", default=None):
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    whisper_json_path = os.path.join(BASE_DIR, 'locale', 'System', 'whisper_languages.json')
    active_dir = os.path.join(BASE_DIR, 'locale', 'Active')
    settings_path = os.path.join(BASE_DIR, "Settings", "settings.json")

    def save_settings(settings_dict):
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings_dict, f, ensure_ascii=False, indent=2)

    # --------------------------
    # Load Whisper languages
    # --------------------------
    if not os.path.isfile(whisper_json_path):
        print(Fore.RED + messages.TRANSCR_whisper_json_missing.format(path=whisper_json_path) + Style.RESET_ALL)
        return None

    with open(whisper_json_path, 'r', encoding='utf-8') as f:
        whisper_langs = json.load(f)

    all_langs = list(whisper_langs.keys())
    
    # --------------------------
    # Filtro lingue per traduzione
    # --------------------------
    # Carica lingue Helsinki
    helsinki_json_path = os.path.join(BASE_DIR, 'locale', 'supported_languages.json')
    if os.path.isfile(helsinki_json_path):
        with open(helsinki_json_path, 'r', encoding='utf-8') as f:
            helsinki_langs = json.load(f)
    else:
        helsinki_langs = {}
        if context in ("translation_source", "translation_target"):
            print(Fore.RED + "Warning: file lingue Helsinki non trovato, nessun filtro applicato" + Style.RESET_ALL)

    # Filtra solo per menu di traduzione
    if context in ("translation_source", "translation_target") and helsinki_langs:
        if context == "translation_source":
            # Mantieni solo lingue presenti in Helsinki (sorgenti)
            all_langs = [lang for lang in all_langs if lang in helsinki_langs and helsinki_langs[lang]]
        elif context == "translation_target" and settings:
            # Lingua sorgente selezionata
            src_lang = settings.get("Translation_Source_Lang")
            valid_targets = helsinki_langs.get(src_lang, [])
            all_langs = [lang for lang in all_langs if lang in valid_targets]


    # --------------------------
    # Quick languages (Active)
    # --------------------------
    quick_langs = []
    if os.path.isdir(active_dir):
        for filename in os.listdir(active_dir):
            if filename.endswith(".json"):
                code = os.path.splitext(filename)[0]
                if code in all_langs:
                    quick_langs.append(code)

    quick_langs = sorted(quick_langs, key=lambda x: getattr(messages, f"LANG_{x}", whisper_langs[x]).lower())
    all_langs = sorted(all_langs, key=lambda x: getattr(messages, f"LANG_{x}", whisper_langs[x]).lower())

    # --------------------------
    # Context → settings key
    # --------------------------
    key_map = {
        "transcription_source": "Transcript_Audio_Spoken_Lang",
        "transcription_target": "Transcript_Target_Lang",
        "translation_source": "Translation_Source_Lang",
        "translation_target": "Translation_Target_Lang"
    }

    settings_key = key_map.get(context)
    
    # Scegli l'header corretto in base al context
    if context == "translation_source":
        header_key = "TRANSLATE_select_source_language_header"
    elif context == "translation_target":
        header_key = "TRANSLATE_select_target_language_header"
    else:
        header_key = "TRANSCR_select_language_header"  # rimane per trascrizione



    if not default and settings and settings_key:
        default = settings.get(settings_key)

    # ==========================
    # Quick menu
    # ==========================
    if quick_langs:
        print()
        print(Fore.YELLOW + getattr(messages, header_key) + " (" + messages.TRANSCR_quick_menu + "):")

        for i, lang in enumerate(quick_langs, start=1):
            name = getattr(messages, f"LANG_{lang}", whisper_langs[lang])
            print(f"{i}. {name}")

        print(f"{len(quick_langs) + 1}. {messages.TRANSCR_show_all_languages}")
        print(f"0. {messages.TRANSCR_select_audio_cancel}")

        while True:
            prompt = messages.TRANSCR_select_language_prompt
            if default:
                default_name = getattr(messages, f"LANG_{default}", whisper_langs[default])
                prompt += f" (\033[93mdefault: {default_name}\033[0m)"

            choice = input(prompt + ": ").strip()

            if not choice and default:
                selected_lang = default
            elif choice.isdigit():
                choice = int(choice)
                if choice == 0:
                    return None
                elif choice == len(quick_langs) + 1:
                    break
                elif 1 <= choice <= len(quick_langs):
                    selected_lang = quick_langs[choice - 1]
                else:
                    print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)
                    continue
            else:
                print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)
                continue

            lang_display = getattr(messages, f"LANG_{selected_lang}", whisper_langs[selected_lang])
            print(Fore.GREEN + messages.TRANSCR_selected_language.format(lang=lang_display) + Style.RESET_ALL)

            if settings and settings_key:
                settings[settings_key] = selected_lang
                save_settings(settings)
            
            print(Fore.MAGENTA + "---------------- DEBUG LANGUAGE STATE ----------------")
            print(Fore.MAGENTA + f"[DEBUG] Context: {context}")
            print(Fore.MAGENTA + f"[DEBUG] Selected language: {selected_lang}")

            print(Fore.MAGENTA + f"[DEBUG] Transcript_Audio_Spoken_Lang: {settings.get('Transcript_Audio_Spoken_Lang')}")
            print(Fore.MAGENTA + f"[DEBUG] Transcript_Target_Lang: {settings.get('Transcript_Target_Lang')}")
            print(Fore.MAGENTA + f"[DEBUG] Translation_Source_Lang: {settings.get('Translation_Source_Lang')}")
            print(Fore.MAGENTA + f"[DEBUG] Translation_Target_Lang: {settings.get('Translation_Target_Lang')}")

            print(Fore.MAGENTA + "------------------------------------------------------" + Style.RESET_ALL)

            return selected_lang

    # ==========================
    # Full menu
    # ==========================
    print("\n" + getattr(messages, header_key) + " (" + messages.TRANSCR_full_menu + "):\n")

    display_names = [getattr(messages, f"LANG_{lang}", whisper_langs[lang]) for lang in all_langs]

    cols, _ = shutil.get_terminal_size(fallback=(80, 24))
    max_len = max(len(name) for name in display_names) + 6
    num_cols = max(1, cols // max_len)
    num_rows = (len(display_names) + num_cols - 1) // num_cols

    for row in range(num_rows):
        row_items = []
        for col in range(num_cols):
            idx = row + col * num_rows
            if idx < len(display_names):
                entry = f"{idx + 1}. {display_names[idx]}"
                row_items.append(entry.ljust(max_len))
        print("".join(row_items))

    print(f"0. {messages.TRANSCR_select_audio_cancel}\n")

    while True:
        prompt = messages.TRANSCR_select_language_prompt
        if default:
            default_name = getattr(messages, f"LANG_{default}", whisper_langs[default])
            prompt += f" (\033[93mdefault: {default_name}\033[0m)"

        choice = input(prompt + ": ").strip()

        if not choice and default:
            selected_lang = default
        elif choice.isdigit():
            choice = int(choice)
            if choice == 0:
                return None
            elif 1 <= choice <= len(all_langs):
                selected_lang = all_langs[choice - 1]
            else:
                print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)
                continue
        else:
            print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)
            continue

        lang_display = getattr(messages, f"LANG_{selected_lang}", whisper_langs[selected_lang])
        print(Fore.GREEN + messages.TRANSCR_selected_language.format(lang=lang_display) + Style.RESET_ALL)

        if settings and settings_key:
            settings[settings_key] = selected_lang
            save_settings(settings)

        print(Fore.MAGENTA + "---------------- DEBUG LANGUAGE STATE ----------------")
        print(Fore.MAGENTA + f"[DEBUG] Context: {context}")
        print(Fore.MAGENTA + f"[DEBUG] Selected language: {selected_lang}")

        print(Fore.MAGENTA + f"[DEBUG] Transcript_Audio_Spoken_Lang: {settings.get('Transcript_Audio_Spoken_Lang')}")
        print(Fore.MAGENTA + f"[DEBUG] Transcript_Target_Lang: {settings.get('Transcript_Target_Lang')}")
        print(Fore.MAGENTA + f"[DEBUG] Translation_Source_Lang: {settings.get('Translation_Source_Lang')}")
        print(Fore.MAGENTA + f"[DEBUG] Translation_Target_Lang: {settings.get('Translation_Target_Lang')}")

        print(Fore.MAGENTA + "------------------------------------------------------" + Style.RESET_ALL)

        return selected_lang

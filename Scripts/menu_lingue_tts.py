# =========================================================
# 1.0 menu_lingue_tts.py
# Selezione lingua per TTS basata su voices_index.json
# =========================================================

import os
import json
from collections import Counter
from colorama import Fore, Style


def seleziona_lingua_tts(messages):
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    voices_json_path = os.path.join(BASE_DIR, "voices", "voices_index.json")

    # --------------------------
    # 1.1 Load voices index
    # --------------------------
    if not os.path.isfile(voices_json_path):
        print(Fore.RED + messages.menu_lingue_TTS_error_voices_file_missing.format(path=voices_json_path) + Style.RESET_ALL)
        return None

    with open(voices_json_path, "r", encoding="utf-8") as f:
        voices_index = json.load(f)

    if not voices_index:
        print(Fore.RED + messages.menu_lingue_TTS_error_no_voices_available + Style.RESET_ALL)
        return None

    # 1.2 Estrazione lingue raggruppate per lingua principale
    all_langs = sorted(set(v["language"].lower() for v in voices_index))
    lang_counts = Counter(v["language"].lower() for v in voices_index)

    if not all_langs:
        print(Fore.RED + messages.menu_lingue_TTS_error_no_languages_available + Style.RESET_ALL)
        return None

    # --------------------------
    # 1.3 Header
    # --------------------------
    print(messages.menu_lingue_TTS_select_language_header)
    print()

    # --------------------------
    # 1.4 Lista lingue migliorata (allineamento corretto)
    # --------------------------
    # Costruisci lista delle lingue con conteggio e nome esteso
    lang_display_list = []
    for lang in all_langs:
        count = lang_counts.get(lang, 0)
        # Nome esteso della lingua (via messages), fallback a codice lingua se non disponibile
        lang_name = getattr(messages, f"LANG_{lang}", lang)
        lang_display_list.append((lang, lang_name, count))

    # Dividi lista in due colonne
    half = (len(lang_display_list) + 1) // 2
    col1 = lang_display_list[:half]
    col2 = lang_display_list[half:]

    # Calcola larghezze massime dinamiche
    max_index_len = len(str(len(lang_display_list))) + 1        # per numeri indice
    max_code_len = max(len(lang) for lang, _, _ in lang_display_list)
    max_name_len = max(len(name) for _, name, _ in lang_display_list)
    # max_count_len calcola solo la parte numerica, parola "voci" viene aggiunta separatamente
    max_count_len = max(len(str(count)) for _, _, count in lang_display_list)

    # stampa lista lingue con allineamento
    for i in range(half):
        # Colonna 1
        code1, name1, count1 = col1[i]
        index1_str = f"{i+1}.".ljust(max_index_len)
        code1_str = code1.ljust(max_code_len)
        name1_str = name1.ljust(max_name_len)
        count1_str = f"{str(count1).rjust(max_count_len)} {messages.menu_lingue_TTS_available_voices}"
        col1_str = f"{index1_str} {code1_str} → {name1_str} ({count1_str})"

        # Colonna 2 (verifica se esiste)
        if i < len(col2):
            code2, name2, count2 = col2[i]
            index2_str = f"{i+1+half}.".ljust(max_index_len)
            code2_str = code2.ljust(max_code_len)
            name2_str = name2.ljust(max_name_len)
            count2_str = f"{str(count2).rjust(max_count_len)} {messages.menu_lingue_TTS_available_voices}"
            col2_str = f"{index2_str} {code2_str} → {name2_str} ({count2_str})"
            print(f"{col1_str}    {col2_str}")
        else:
            print(col1_str)
            
    print()
    print(messages.menu_lingue_TTS_cancel_option)
    print()

    # --------------------------
    # 1.5 Input utente
    # --------------------------
    while True:
        choice = input(messages.menu_lingue_TTS_select_language_prompt + ": ").strip()

        # Cancel
        if choice == "0":
            return None

        # Selezione da lista
        if choice.isdigit():
            choice_int = int(choice)
            if 1 <= choice_int <= len(all_langs):
                selected_lang = all_langs[choice_int - 1]
                break
            else:
                print(Fore.RED + messages.menu_lingue_TTS_invalid_choice + Style.RESET_ALL)
                continue

        # Inserimento manuale disabilitato
        elif choice:
            print(Fore.RED + messages.menu_lingue_TTS_invalid_choice + Style.RESET_ALL)
            continue
        else:
            print(Fore.RED + messages.menu_lingue_TTS_invalid_choice + Style.RESET_ALL)

    # --------------------------
    # 1.6 Validazione
    # --------------------------
    if selected_lang not in all_langs:
        print(Fore.RED + messages.menu_lingue_TTS_error_language_not_supported.format(lang=selected_lang) + Style.RESET_ALL)
        return None

    # --------------------------
    # 1.7 Output finale
    # --------------------------
    print(Fore.GREEN + messages.menu_lingue_TTS_selected_language.format(lang=selected_lang) + Style.RESET_ALL)
    
    print(Fore.MAGENTA + "----- DEBUG TTS LANGUAGE -----" + Style.RESET_ALL)
    print(Fore.MAGENTA + f"[DEBUG] selected_lang: {selected_lang}" + Style.RESET_ALL)
    print(Fore.MAGENTA + f"[DEBUG] type: {type(selected_lang)}" + Style.RESET_ALL)
    print(Fore.MAGENTA + "------------------------------" + Style.RESET_ALL)
    
    return selected_lang


# =========================================================
# 1.8 MAIN per test standalone
# =========================================================
if __name__ == "__main__":
    import sys
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.append(str(BASE_DIR / "core"))

    from messages import Messages

    messages = Messages()
    seleziona_lingua_tts(messages)
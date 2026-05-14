# =========================================================
# backup_utils.py
# =========================================================

import os
import shutil
from colorama import Fore, Style
from send2trash import send2trash


def manage_history(work_dir, settings, messages):
    if not os.path.exists(work_dir):
        print(Fore.RED + messages.BACKUP_ERROR_SOURCE_MISSING.format(source_dir=work_dir) + Style.RESET_ALL)
        return

    all_dirs = [d for d in os.listdir(work_dir) if os.path.isdir(os.path.join(work_dir, d))]
    if not all_dirs:
        print(Fore.YELLOW + messages.BACKUP_NO_FILES + Style.RESET_ALL)
        return

    # Sort folders chronologically
    all_dirs.sort()

    max_backups = settings.get('max_backups', 10)
    max_per_language = settings.get('max_backups_per_language', 10)
    max_size_gb = settings.get('max_folders_size_gb', None)
    use_trash = settings.get('use_trash', False)

    # -------------------------------
    # 1 Group folders by language
    # -------------------------------
    by_language = {}
    for d in all_dirs:
        parts = d.split('_')
        lang = 'unknown'
        for part in parts:
            if not part.replace('-', '').isdigit():  # ignora numeri e trattini
                lang = part
                break
        by_language.setdefault(lang, []).append(d)

    # -------------------------------
    # 2 Limit per language
    # -------------------------------
    for lang, folders in by_language.items():
        print(f"[DEBUG] Language: {lang} | Number of folders: {len(folders)}")
        for f in folders:
            print(f"    {f}")
        folders.sort()
        while len(folders) > max_per_language:
            oldest = folders.pop(0)
            path = os.path.join(work_dir, oldest)
            try:
                if use_trash:
                    send2trash(path)
                else:
                    shutil.rmtree(path)
                print(Fore.YELLOW + messages.BACKUP_OLD_REMOVED.format(old_path=path) + Style.RESET_ALL)
                all_dirs.remove(oldest)
            except Exception as e:
                print(Fore.RED + messages.BACKUP_ERROR_REMOVING.format(old_path=path) + f": {e}" + Style.RESET_ALL)

    # -------------------------------
    # 3 Total backups limit
    # -------------------------------
    all_dirs.sort()
    while len(all_dirs) > max_backups:
        oldest = all_dirs.pop(0)
        path = os.path.join(work_dir, oldest)
        try:
            if use_trash:
                send2trash(path)
            else:
                shutil.rmtree(path)
            print(Fore.YELLOW + messages.BACKUP_OLD_REMOVED.format(old_path=path) + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + messages.BACKUP_ERROR_REMOVING.format(old_path=path) + f": {e}" + Style.RESET_ALL)

    # -------------------------------
    # 4 Size check
    # -------------------------------
    if max_size_gb:
        total_size = 0
        for d in os.listdir(work_dir):
            path = os.path.join(work_dir, d)
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        total_size += os.path.getsize(os.path.join(root, f))
        total_size_gb = total_size / (1024 ** 3)

        if total_size_gb > max_size_gb:
            print(Fore.YELLOW + messages.BACKUP_SIZE_WARNING.format(
                size=f"{total_size_gb:.6f}",
                limit=f"{max_size_gb:.6f}"
            ) + Style.RESET_ALL)

            # Step 1: Ask if user wants to clean up (mandatory input)
            yes_values = (messages.YES_SHORT.lower(), messages.YES_FULL.lower())
            no_values = (messages.NO_SHORT.lower(), messages.NO_FULL.lower())
            proceed_cleanup = False

            while True:
                response = input(
                    Fore.YELLOW + messages.BACKUP_SIZE_CLEAN_PROMPT + f" [{messages.YES_SHORT}/{messages.NO_SHORT}]: " + Style.RESET_ALL
                ).strip().lower()
                if response in yes_values:
                    proceed_cleanup = True
                    break
                elif response in no_values:
                    proceed_cleanup = False
                    break
                else:
                    print(Fore.RED + messages.SETTINGS_INVALID_VALUE + Style.RESET_ALL)

            if proceed_cleanup:
                # Step 2: Ask how to delete (definitivo o cestino)
                while True:
                    response = input(
                        Fore.YELLOW + messages.BACKUP_SIZE_DELETE_METHOD_PROMPT + f" [{messages.BACKUP_SIZE_DELETE_METHOD_DEF[0]}/{messages.BACKUP_SIZE_DELETE_METHOD_TRASH[0]}]: " + Style.RESET_ALL
                    ).strip().lower()
                    if response in (messages.BACKUP_SIZE_DELETE_METHOD_DEF.lower(), messages.BACKUP_SIZE_DELETE_METHOD_DEF[0].lower()):
                        use_trash_local = False
                        break
                    elif response in (messages.BACKUP_SIZE_DELETE_METHOD_TRASH.lower(), messages.BACKUP_SIZE_DELETE_METHOD_TRASH[0].lower()):
                        use_trash_local = True
                        break
                    else:
                        print(Fore.RED + messages.SETTINGS_INVALID_VALUE + Style.RESET_ALL)

                # Step 3: Delete oldest folders until under limit
                all_dirs.sort()
                idx = 0
                while total_size_gb > max_size_gb and idx < len(all_dirs):
                    path_to_remove = os.path.join(work_dir, all_dirs[idx])
                    try:
                        if use_trash_local:
                            send2trash(path_to_remove)
                        else:
                            shutil.rmtree(path_to_remove)
                        print(Fore.YELLOW + messages.BACKUP_OLD_REMOVED.format(old_path=path_to_remove) + Style.RESET_ALL)

                        # Recalculate total size
                        total_size = 0
                        for d in os.listdir(work_dir):
                            path_check = os.path.join(work_dir, d)
                            if os.path.isdir(path_check):
                                for root, _, files in os.walk(path_check):
                                    for f in files:
                                        total_size += os.path.getsize(os.path.join(root, f))
                        total_size_gb = total_size / (1024 ** 3)
                    except Exception as e:
                        print(Fore.RED + messages.BACKUP_ERROR_REMOVING.format(old_path=path_to_remove) + f": {e}" + Style.RESET_ALL)
                    idx += 1
            else:
                print(Fore.CYAN + messages.BACKUP_SIZE_MANUAL_CHECK + Style.RESET_ALL)

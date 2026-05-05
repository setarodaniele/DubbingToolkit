# =========================================================
# file_selector.py
# Funzioni generiche per selezione file e cartelle
# =========================================================

from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from core.ui_printer import print_error, print_info
from core.ui_colors import COLOR_ERROR, COLOR_INFO
import os

def select_input_file(messages, initial_folder: Path = None, file_types=None) -> Path | None:
    """
    Seleziona un singolo file da una cartella predefinita o tramite dialogo manuale.
    - messages: istanza Messages centralizzata
    - initial_folder: cartella di partenza
    - file_types: lista di tuple per tipi di file es. [("SRT files", "*.srt")]
    """
    initial_folder = initial_folder or Path.cwd()
    file_types = file_types or [("All files", "*.*")]
    
    try:
        Tk().withdraw()  # Nasconde la finestra principale Tkinter
        file_path = askopenfilename(
            title=messages.FILE_SELECTOR_dialog_title_input,
            initialdir=str(initial_folder),
            filetypes=file_types
        )
        if not file_path:
            print_info(messages.FILE_SELECTOR_selection_cancelled)
            return None
        return Path(file_path)
    except Exception as e:
        print_error(f"{messages.FILE_SELECTOR_error_generic}: {e}", color=COLOR_ERROR)
        return None

def select_input_folder(messages, initial_folder: Path = None) -> Path | None:
    """
    Seleziona una cartella di input.
    - messages: istanza Messages centralizzata
    """
    initial_folder = initial_folder or Path.cwd()
    
    try:
        Tk().withdraw()
        folder_path = askdirectory(
            title=messages.FILE_SELECTOR_dialog_title_input_folder,
            initialdir=str(initial_folder)
        )
        if not folder_path:
            print_info(messages.FILE_SELECTOR_selection_cancelled)
            return None
        return Path(folder_path)
    except Exception as e:
        print_error(f"{messages.FILE_SELECTOR_error_generic}: {e}", color=COLOR_ERROR)
        return None

def select_output_folder(messages, initial_folder: Path = None) -> Path | None:
    """
    Seleziona una cartella di output.
    - messages: istanza Messages centralizzata
    """
    initial_folder = initial_folder or Path.cwd()
    
    try:
        Tk().withdraw()
        folder_path = askdirectory(
            title=messages.FILE_SELECTOR_dialog_title_output_folder,
            initialdir=str(initial_folder)
        )
        if not folder_path:
            print_info(messages.FILE_SELECTOR_selection_cancelled)
            return None
        return Path(folder_path)
    except Exception as e:
        print_error(f"{messages.FILE_SELECTOR_error_generic}: {e}", color=COLOR_ERROR)
        return None

def select_file_menu(messages, base_folder: Path, file_types=None) -> Path | None:
    """
    Menu interattivo per selezione file in base a cartella principale.
    - messages: istanza Messages centralizzata
    - base_folder: cartella di riferimento (Translated, Transcript, ecc.)
    - file_types: lista di tuple per tipi di file, es. [("SRT files", "*.srt")]
    """
    file_types = file_types or [("All files", "*.*")]

    while True:
        print("\n" + messages.FILE_SELECTOR_MenuDivider)
        print(messages.FILE_SELECTOR_MenuTitle.format(folder_name=base_folder.name))
        print("1. " + messages.FILE_SELECTOR_Option_FromFolder.format(folder_name=base_folder.name))
        print("2. " + messages.FILE_SELECTOR_Option_LastWorkFile)
        print("3. " + messages.FILE_SELECTOR_Option_Manual)
        print("4. " + messages.FILE_SELECTOR_Option_Exit)
        scelta = input(messages.FILE_SELECTOR_PromptSelect).strip()

        # ----------------------------
        # OPZIONE 1: Scegli da sottocartelle
        # ----------------------------
        if scelta == "1":
            subfolders = [f for f in base_folder.iterdir() if f.is_dir()]
            if not subfolders:
                print(messages.FILE_SELECTOR_NoFoldersFound)
                continue
            subfolders.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # Mostra sottocartelle
            for idx, f in enumerate(subfolders, start=1):
                print(f"{idx}. {f.name}")
            sel = input(messages.FILE_SELECTOR_PromptFileNumber).strip()
            if sel.isdigit() and 1 <= int(sel) <= len(subfolders):
                chosen_folder = subfolders[int(sel) - 1]
                # Filtra file work SRT
                work_files = [f for f in chosen_folder.glob("*work*.srt") if f.is_file()]
                if not work_files:
                    print(messages.FILE_SELECTOR_NoWorkFiles)
                    continue
                work_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                return work_files[0]
            else:
                print(messages.FILE_SELECTOR_InvalidSelection)

        # ----------------------------
        # OPZIONE 2: Ultimo file work
        # ----------------------------
        elif scelta == "2":
            subfolders = [f for f in base_folder.iterdir() if f.is_dir()]
            if not subfolders:
                print(messages.FILE_SELECTOR_NoFoldersFound)
                continue
            subfolders.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            last_folder = subfolders[0]
            work_files = [f for f in last_folder.glob("*work*.srt") if f.is_file()]
            if not work_files:
                print(messages.FILE_SELECTOR_NoWorkFiles)
                continue
            work_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            return work_files[0]

        # ----------------------------
        # OPZIONE 3: Selezione manuale
        # ----------------------------
        elif scelta == "3":
            from tkinter import Tk
            from tkinter.filedialog import askopenfilename
            try:
                Tk().withdraw()
                file_path = askopenfilename(
                    title=messages.FILE_SELECTOR_dialog_title_input,
                    initialdir=str(base_folder),
                    filetypes=file_types
                )
                if file_path:
                    return Path(file_path)
                else:
                    print(messages.FILE_SELECTOR_selection_cancelled)
                    return None
            except Exception as e:
                print(messages.FILE_SELECTOR_error_generic.format(error=str(e)))
                return None

        # ----------------------------
        # OPZIONE 4: Esci
        # ----------------------------
        elif scelta == "4":
            return None

        # ----------------------------
        # SCELTA NON VALIDA
        # ----------------------------
        else:
            print(messages.FILE_SELECTOR_InvalidSelection)
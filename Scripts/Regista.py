# =========================================================
# Regista.py
# =========================================================


import sys
import os

# Aggiunge la cartella principale del progetto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.messages import Messages  # classe centrale
from core.api_check import check_tts_status
from core.workspace_manager import WorkspaceManager, WorkspaceError

from pathlib import Path
import json
from colorama import Fore, Style, init
from SilenziaWarning import *
from estrai_tracce import estrai_tracce
from trascrivi_audio import trascrivi_audio
from traduci_testo import traduci_testo
from monitoraggio_consumo import ConsumoTTS
import settings_manager
from settings_manager import default_setting
from core.logger import logger
from core.update_checker import check_for_updates
from core.input_parsing import is_yes
from core.error_reporter import send_error_report, has_errors, create_silent_exit_report
from info_manager import InfoManager



init()
'''
# Load default settings at startup
default_setting(messages=None, preserve_interface_lang=True)

# =========================================================
# Set locale for proper number/character formatting
# =========================================================
try:
    locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Italian_Italy.1252')
'''

# =========================================================
# Project info initialization
# =========================================================
def _init_project_info(ws, name, settings, messages):
    """Write initial project_info.json and project_info.txt for a newly created project."""
    if settings is None:
        return
    try:
        im = InfoManager(ws.root)
        im.update_project(name, settings)
        im.generate_info_file(messages)
    except Exception:
        pass


# =========================================================
# Visual separator
# =========================================================
def print_separator(lines=5):
    """Print blank lines to visually separate menu operations."""
    print("\n" * lines)


# =========================================================
# Title display
# =========================================================
def mostra_titolo_menu(messages, titolo_key, ws=None, width=38):
    """Show a menu title with active project name."""
    C, Y, R = Fore.CYAN, Fore.YELLOW, Style.RESET_ALL
    titolo = getattr(messages, titolo_key, f"[MISSING: {titolo_key}]")
    print("\n" + C + "-" * width + R)
    print(C + titolo + R)
    if ws is not None:
        template = getattr(messages, "RegistaWorkspaceNamed", "[Progetto: {0}]")
        print(Y + template.format(ws.name) + R)
    print(C + "-" * width + R)


# =========================================================
# TTS Engine Selection
# =========================================================
def scegli_motore_tts(messages):
    consumo_google = ConsumoTTS(motore="google")
    consumo_azure = ConsumoTTS(motore="azure")

    print(Fore.YELLOW + "\n" + messages.RegistaTTSConsumption)
    print(f"Google: {consumo_google.dati['google'][consumo_google.data_oggi]} caratteri "
          f"({consumo_google.percentuale_consumo():.1f}% franchigia)")
    print(f"Azure: {consumo_azure.dati['azure'][consumo_azure.data_oggi]} caratteri "
          f"({consumo_azure.percentuale_consumo():.1f}% franchigia)" + Style.RESET_ALL)

    while True:
        print("\n" + messages.RegistaTTSSelect)
        print(messages.RegistaTTSGoogle)
        print(messages.RegistaTTSAzure)
        scelta = input("Scelta (1 o 2): ").strip()
        if scelta == "1":
            return "google"
        elif scelta == "2":
            return "azure"
        else:
            print(messages.RegistaTTSChoiceInvalid)




# =========================================================
# Workspace info box
# =========================================================
def mostra_info_workspace(ws, messages):
    """Print a pipeline status block for the active workspace."""
    W   = 54
    LBL = 17   # label column width including leading space and colon

    C, G, RD, R, D = Fore.CYAN, Fore.GREEN, Fore.RED, Style.RESET_ALL, Style.DIM

    # Load project_info.json
    info = {}
    info_path = ws.root / "project_info.json"
    if info_path.exists():
        try:
            with info_path.open("r", encoding="utf-8") as f:
                info = json.load(f)
        except Exception:
            pass

    def read_stage(stage_name):
        """Return [(track_id, metadata_dict)] for each completed track in a stage."""
        stage_dir = ws.root / stage_name
        results = []
        if not stage_dir.is_dir():
            return results
        for track_dir in sorted(stage_dir.iterdir()):
            if not (track_dir.is_dir() and track_dir.name.startswith("track_")):
                continue
            current = track_dir / "current"
            if not (current.is_dir() and any(current.iterdir())):
                continue
            meta = {}
            meta_path = current / "metadata.json"
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                except Exception:
                    pass
            results.append((track_dir.name, meta))
        return results

    def fmt_row(label, value, ok_status=None):
        lbl = f" {label}:".ljust(LBL)
        suffix = ""
        if ok_status is True:
            suffix = "  " + G + "[OK]" + R
        elif ok_status is False:
            suffix = "  " + RD + "[!]" + R
        return lbl + value + suffix

    def stage_row(tracks, single_detail_fn, many_label):
        if not tracks:
            return "—"
        if len(tracks) == 1:
            return single_detail_fn(tracks[0][0], tracks[0][1])
        return f"{len(tracks)} {many_label}"

    # Collect data
    video_info  = info.get("video_file", {})
    video_src   = video_info.get("file_sorgente", "")
    video_ok    = bool(video_src and Path(video_src).exists())

    audio_input_dir = ws.root / "audio_input"
    audio_files = sorted(audio_input_dir.iterdir()) if audio_input_dir.is_dir() else []
    audio_files = [f for f in audio_files if f.is_file()]

    extraction   = read_stage("audio_extraction")
    transcripts  = read_stage("transcripts")
    translations = read_stage("translated")
    dubbed       = read_stage("dubbed")

    ultima_mod = info.get("progetto", {}).get("ultima_modifica", "")

    has_any = bool(video_src or audio_files or extraction or transcripts or translations or dubbed)
    if not has_any:
        print(C + D + f" {getattr(messages, 'InfoBoxEmptyProject', 'No data yet')}" + R)
        print(C + "-" * W + R)
        return

    rows = []
    max_val = W - LBL - 1

    # Video row
    if video_src:
        fname = Path(video_src).name
        if len(fname) > max_val:
            fname = "…" + fname[-(max_val - 1):]
        rows.append(fmt_row(getattr(messages, "InfoBoxVideo", "Video"), fname, ok_status=video_ok))

    # Audio input row (only if no video, or if files are actually in audio_input)
    if audio_files:
        if len(audio_files) == 1:
            fname = audio_files[0].name
            if len(fname) > max_val:
                fname = "…" + fname[-(max_val - 1):]
            rows.append(fmt_row(getattr(messages, "InfoBoxAudio", "Audio"), fname))
        else:
            rows.append(fmt_row(getattr(messages, "InfoBoxAudio", "Audio"),
                                f"{len(audio_files)} {getattr(messages, 'InfoBoxManyTracks', 'file')}"))

    # Extraction
    rows.append(fmt_row(
        getattr(messages, "InfoBoxExtraction", "Estrazione"),
        stage_row(extraction,
                  lambda tid, m: tid,
                  getattr(messages, "InfoBoxManyTracks", "tracce"))
    ))

    # Transcription
    rows.append(fmt_row(
        getattr(messages, "InfoBoxTranscription", "Trascrizione"),
        stage_row(transcripts,
                  lambda tid, m: f"{tid} · {m['spoken_lang']}" if m.get("spoken_lang") else tid,
                  getattr(messages, "InfoBoxManyTranscriptions", "trascrizioni"))
    ))

    # Translation
    rows.append(fmt_row(
        getattr(messages, "InfoBoxTranslation", "Traduzione"),
        stage_row(translations,
                  lambda tid, m: (f"{tid} · {m['source_lang']} → {m['target_lang']}"
                                  if m.get("source_lang") and m.get("target_lang") else tid),
                  getattr(messages, "InfoBoxManyTranslations", "traduzioni"))
    ))

    # Dubbing
    rows.append(fmt_row(
        getattr(messages, "InfoBoxDubbing", "Doppiaggio"),
        stage_row(dubbed,
                  lambda tid, m: (f"{tid} · {m.get('lang', m.get('target_lang', ''))}"
                                  if m.get("lang") or m.get("target_lang") else tid),
                  getattr(messages, "InfoBoxManyDubbed", "doppiaggi"))
    ))

    for row in rows:
        print(row)

    if ultima_mod:
        print(C + D + f" {getattr(messages, 'InfoBoxModified', 'Modificato')}: {ultima_mod}" + R)

    print(C + "-" * W + R)


# =========================================================
# Menu display
# =========================================================
def menu(messages, tts_enabled):
    """Display main workflow menu options."""
    print(getattr(messages, "RegistaMenuOption0", "0. Manage projects"))
    print("-"*28)
    print(messages.RegistaMenuOption1)
    print(messages.RegistaMenuOption2)
    print(messages.RegistaMenuOption3)

    # Opzione 4: colore a seconda della disponibilità TTS
    if tts_enabled:
        print(messages.RegistaMenuOption4)
    else:
        print(Fore.LIGHTBLACK_EX + messages.RegistaMenuOption4 + " (Disabilitato)" + Style.RESET_ALL)

    print("-"*28)
    print(messages.RegistaMenuOption8)
    print(getattr(messages, "RegistaMenuOptionR", "R. Send error report"))
    print(getattr(messages, "RegistaMenuOptionQ", "X. Exit"))

    scelta = input(messages.RegistaMenuPrompt + " ").strip()

    # Blocca selezione opzione 4 se TTS disabilitato
    if scelta == "4" and not tts_enabled:
        print(Fore.YELLOW + messages.RegistaMenuOption4Disabled + Style.RESET_ALL)
        return None

    return scelta


# =========================================================
# Project selection / creation at startup
# =========================================================
def _suggest_project_name() -> str:
    """Return an available auto-generated project name based on today's date.

    Appends _2, _3, ... if the base name already exists.
    """
    from datetime import date
    base = date.today().strftime("%Y-%m-%d")
    existing = set(WorkspaceManager.list_projects())
    if base not in existing:
        return base
    n = 2
    while f"{base}_{n}" in existing:
        n += 1
    return f"{base}_{n}"


def seleziona_o_crea_progetto(messages, settings=None) -> "WorkspaceManager":
    """Prompt user to select an existing project or create a new one.

    Called at startup when no project is active, and after close/delete.
    Always returns an active WorkspaceManager.
    """
    W = 38
    C, Y, G, R = Fore.CYAN, Fore.YELLOW, Fore.GREEN, Style.RESET_ALL

    while True:
        projects = WorkspaceManager.list_projects()
        default_name = _suggest_project_name()

        print("\n" + C + "-" * W + R)
        print(Y + " " + getattr(messages, "RegistaNoProject", "Nessun progetto attivo.") + R)
        print(C + "-" * W + R)

        if projects:
            print(G + " " + getattr(messages, "ProgettiList", "Progetti disponibili:") + R)
            for i, name in enumerate(projects, 1):
                print(f"   {i}. {name}")
            print(C + "-" * W + R)

        prompt = getattr(messages, "RegistaSelectOrCreate",
                         "Seleziona numero o nome nuovo progetto (Invio: \"{0}\"):").format(default_name)
        raw = input(" " + prompt + " ").strip()

        if not raw:
            raw = default_name

        # Number input → select existing project
        if raw.isdigit() and projects:
            idx = int(raw) - 1
            if 0 <= idx < len(projects):
                try:
                    ws = WorkspaceManager.open_project(projects[idx])
                    msg = getattr(messages, "RegistaLoadedProject", "Progetto caricato: {0}").format(ws.name)
                    print(G + msg + R)
                    return ws
                except WorkspaceError as e:
                    print(Fore.RED + str(e) + R)
                    continue
            else:
                print(Y + getattr(messages, "ProgettiInvalid", "Scelta non valida.") + R)
                continue

        # Name input → create new, or offer to open if already exists
        if raw in WorkspaceManager.list_projects():
            prompt = getattr(messages, "ProgettiExistsPrompt",
                             "'{0}': progetto già esistente. Aprirlo? (s/n)").format(raw)
            answer = input(prompt + " ").strip()
            if is_yes(answer, messages):
                try:
                    ws = WorkspaceManager.open_project(raw)
                    msg = getattr(messages, "ProgettiOpenOk", "Progetto '{0}' aperto.").format(raw)
                    print(G + msg + R)
                    return ws
                except WorkspaceError as e:
                    print(Fore.RED + str(e) + R)
        else:
            try:
                ws = WorkspaceManager.create_project(raw)
                _init_project_info(ws, raw, settings, messages)
                msg = getattr(messages, "ProgettiCreateOk", "Progetto '{0}' creato.").format(raw)
                print(G + msg + R)
                return ws
            except WorkspaceError as e:
                print(Fore.RED + str(e) + R)


# =========================================================
# Gestione Progetti sub-menu
# =========================================================
def gestione_progetti(messages, ws, settings=None):
    """Project management sub-menu. Returns the (possibly updated) workspace, or None."""
    while True:
        projects = WorkspaceManager.list_projects()

        print("\n" + Fore.CYAN + "="*38)
        print(getattr(messages, "ProgettiTitle", "Gestione Progetti"))
        if ws is not None:
            active_label = getattr(messages, "ProgettiActive", "Attivo: {0}")
            print(Fore.YELLOW + active_label.format(ws.name) + Style.RESET_ALL + Fore.CYAN)
        else:
            print(Fore.LIGHTBLACK_EX + getattr(messages, "RegistaNoProject", "No active project.") + Style.RESET_ALL + Fore.CYAN)
        print("="*38 + Style.RESET_ALL)

        # List existing projects with frame
        print()
        project_count = len(projects) if projects else 0
        projects_label = getattr(messages, "ProgettiListLabel", "PROGETTI DISPONIBILI")
        print(Fore.CYAN + projects_label + f" - {project_count}" + Style.RESET_ALL)
        print(Fore.CYAN + "-"*38 + Style.RESET_ALL)

        if projects:
            for i, name in enumerate(projects, 1):
                marker = " *" if ws is not None and name == ws.name else ""
                print(f"  {i}. {name}{marker}")
        else:
            print(Fore.LIGHTBLACK_EX + getattr(messages, "ProgettiNone", "No named projects yet.") + Style.RESET_ALL)

        print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
        print()
        options_label = getattr(messages, "ProgettiOptionsLabel", "OPERAZIONI GESTIONE PROGETTI")
        print(Fore.CYAN + options_label + Style.RESET_ALL)
        print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
        print(getattr(messages, "ProgettiOpt1", "1. New project"))
        print(getattr(messages, "ProgettiOpt2", "2. Select project"))
        print(getattr(messages, "ProgettiOpt3", "3. Delete project"))
        print(getattr(messages, "ProgettiOpt4", "4. Duplicate project"))
        print(getattr(messages, "ProgettiOpt5", "5. Rename project"))
        print(getattr(messages, "ProgettiOpt6", "6. Open folder in Explorer"))
        print(getattr(messages, "ProgettiOpt0", "0. Back"))
        print(Fore.CYAN + "="*38 + Style.RESET_ALL)

        scelta = input(getattr(messages, "ProgettiPrompt", "Choose:") + " ").strip()

        if scelta == "1":
            suggested = _suggest_project_name()
            prompt = getattr(messages, "ProgettiNamePrompt", "Nome progetto (lettere, numeri, _ - soltanto):")
            raw = input(f"{prompt} (Invio: \"{suggested}\"): ").strip()
            name = raw if raw else suggested
            try:
                ws = WorkspaceManager.create_project(name)
                _init_project_info(ws, name, settings, messages)
                print(Fore.GREEN + getattr(messages, "ProgettiCreateOk", "Project '{0}' created.").format(name) + Style.RESET_ALL)
                break
            except WorkspaceError as e:
                print(Fore.RED + getattr(messages, "ProgettiError", "Error: {0}").format(e) + Style.RESET_ALL)

        elif scelta == "2":
            if not projects:
                print(Fore.YELLOW + getattr(messages, "ProgettiNone", "No named projects yet.") + Style.RESET_ALL)
                continue
            print()
            select_label = getattr(messages, "ProgettiSelectLabel", "SELEZIONA PROGETTO")
            print(Fore.CYAN + select_label + f" - {len(projects)}" + Style.RESET_ALL)
            print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
            for i, name in enumerate(projects, 1):
                print(f"  {i}. {name}")
            print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
            sel = input(getattr(messages, "ProgettiPrompt", "Choose:") + " ").strip()
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(projects):
                    ws = WorkspaceManager.open_project(projects[idx])
                    print(Fore.GREEN + getattr(messages, "ProgettiOpenOk", "Project '{0}' is now active.").format(projects[idx]) + Style.RESET_ALL)
                    break
                else:
                    print(Fore.YELLOW + getattr(messages, "ProgettiInvalid", "Invalid choice.") + Style.RESET_ALL)
            except (ValueError, WorkspaceError) as e:
                print(Fore.RED + getattr(messages, "ProgettiError", "Error: {0}").format(e) + Style.RESET_ALL)

        elif scelta == "3":
            if not projects:
                print(Fore.YELLOW + getattr(messages, "ProgettiNone", "No named projects yet.") + Style.RESET_ALL)
                continue
            print()
            delete_label = getattr(messages, "ProgettiDeleteLabel", "ELIMINA PROGETTO")
            print(Fore.CYAN + delete_label + f" - {len(projects)}" + Style.RESET_ALL)
            print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
            for i, name in enumerate(projects, 1):
                print(f"  {i}. {name}")
            print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
            sel = input(getattr(messages, "ProgettiPrompt", "Choose:") + " ").strip()
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(projects):
                    target = projects[idx]
                    use_trash = bool((settings or {}).get("use_trash", False))
                    if use_trash:
                        confirm_msg = getattr(messages, "ProgettiDeleteConfirmTrash", "Move '{0}' to Trash? (y/n):").format(target)
                    else:
                        confirm_msg = getattr(messages, "ProgettiDeleteConfirm", "Delete '{0}'? Irreversible. (y/n):").format(target)
                    confirm = input(confirm_msg + " ").strip()
                    if is_yes(confirm, messages):
                        WorkspaceManager.delete_project(target, use_trash=use_trash)
                        if use_trash:
                            ok_msg = getattr(messages, "ProgettiDeleteOkTrash", "Project '{0}' moved to Trash.").format(target)
                        else:
                            ok_msg = getattr(messages, "ProgettiDeleteOk", "Project '{0}' deleted.").format(target)
                        print(Fore.GREEN + ok_msg + Style.RESET_ALL)
                        ws = WorkspaceManager.get_active()
                    else:
                        print(Fore.YELLOW + getattr(messages, "ProgettiDeleteAborted", "Deletion aborted.") + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + getattr(messages, "ProgettiInvalid", "Invalid choice.") + Style.RESET_ALL)
            except (ValueError, WorkspaceError) as e:
                print(Fore.RED + getattr(messages, "ProgettiError", "Error: {0}").format(e) + Style.RESET_ALL)
            except PermissionError:
                print(Fore.RED + "Cannot delete: folder is open in Explorer or locked by another process. Close it and try again." + Style.RESET_ALL)

        elif scelta == "4":
            if not projects:
                print(Fore.YELLOW + getattr(messages, "ProgettiNone", "No named projects yet.") + Style.RESET_ALL)
                continue
            print()
            dup_label = getattr(messages, "ProgettiDuplicateLabel", "DUPLICA PROGETTO")
            print(Fore.CYAN + dup_label + f" - {len(projects)}" + Style.RESET_ALL)
            print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
            for i, name in enumerate(projects, 1):
                print(f"  {i}. {name}")
            print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
            sel = input(getattr(messages, "ProgettiPrompt", "Choose:") + " ").strip()
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(projects):
                    source = projects[idx]
                    suggested = source + "_copy"
                    prompt = getattr(messages, "ProgettiDuplicatePrompt", "New project name:")
                    raw = input(f"{prompt} (Invio: \"{suggested}\"): ").strip()
                    dest = raw if raw else suggested
                    ws_dup = WorkspaceManager.duplicate_project(source, dest)
                    _init_project_info(ws_dup, dest, settings, messages)
                    print(Fore.GREEN + getattr(messages, "ProgettiDuplicateOk", "Project '{0}' duplicated as '{1}'.").format(source, dest) + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + getattr(messages, "ProgettiInvalid", "Invalid choice.") + Style.RESET_ALL)
            except (ValueError, WorkspaceError) as e:
                print(Fore.RED + getattr(messages, "ProgettiError", "Error: {0}").format(e) + Style.RESET_ALL)
            except PermissionError:
                print(Fore.RED + "Cannot duplicate: source folder is open in Explorer or locked by another process. Close it and try again." + Style.RESET_ALL)

        elif scelta == "5":
            if not projects:
                print(Fore.YELLOW + getattr(messages, "ProgettiNone", "No named projects yet.") + Style.RESET_ALL)
                continue
            print()
            rename_label = getattr(messages, "ProgettiRenameLabel", "RINOMINA PROGETTO")
            print(Fore.CYAN + rename_label + f" - {len(projects)}" + Style.RESET_ALL)
            print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
            for i, name in enumerate(projects, 1):
                print(f"  {i}. {name}")
            print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
            sel = input(getattr(messages, "ProgettiPrompt", "Choose:") + " ").strip()
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(projects):
                    old_name = projects[idx]
                    prompt = getattr(messages, "ProgettiRenamePrompt", "New name:")
                    new_name = input(f"{prompt} ").strip()
                    if new_name:
                        ws = WorkspaceManager.rename_project(old_name, new_name)
                        InfoManager(ws.root).record_rename(old_name, new_name)
                        _init_project_info(ws, new_name, settings, messages)
                        print(Fore.GREEN + getattr(messages, "ProgettiRenameOk", "Project '{0}' renamed to '{1}'.").format(old_name, new_name) + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + getattr(messages, "ProgettiInvalid", "Invalid choice.") + Style.RESET_ALL)
            except (ValueError, WorkspaceError) as e:
                print(Fore.RED + getattr(messages, "ProgettiError", "Error: {0}").format(e) + Style.RESET_ALL)
            except PermissionError:
                print(Fore.RED + "Cannot rename: folder is open in Explorer or locked by another process. Close it and try again." + Style.RESET_ALL)

        elif scelta == "6":
            if not projects:
                print(Fore.YELLOW + getattr(messages, "ProgettiNone", "No named projects yet.") + Style.RESET_ALL)
                continue
            print()
            open_label = getattr(messages, "ProgettiOpenFolderLabel", "APRI CARTELLA")
            print(Fore.CYAN + open_label + f" - {len(projects)}" + Style.RESET_ALL)
            print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
            for i, name in enumerate(projects, 1):
                print(f"  {i}. {name}")
            print(Fore.CYAN + "-"*38 + Style.RESET_ALL)
            sel = input(getattr(messages, "ProgettiPrompt", "Choose:") + " ").strip()
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(projects):
                    import os as _os
                    folder = WorkspaceManager(projects[idx]).root
                    _os.startfile(str(folder))
                else:
                    print(Fore.YELLOW + getattr(messages, "ProgettiInvalid", "Invalid choice.") + Style.RESET_ALL)
            except (ValueError, Exception) as e:
                print(Fore.RED + getattr(messages, "ProgettiError", "Error: {0}").format(e) + Style.RESET_ALL)

        elif scelta == "0":
            break
        else:
            print(Fore.YELLOW + getattr(messages, "ProgettiInvalid", "Invalid choice.") + Style.RESET_ALL)

    return ws

# =========================================================
# Main program loop
# =========================================================
def main(messages):
    RESET_FILE = Path.cwd() / "Settings" / "reset.json"
    SETTINGS_FILE = Path.cwd() / "Settings" / "settings.json"

    def load_reset_flags():
        with RESET_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_reset_flags(data):
        with RESET_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Controllo primo avvio
    '''
    reset_flags = load_reset_flags()
    if reset_flags.get("first_launch", True):
        default_setting(messages)
        reset_flags["first_launch"] = False
        save_reset_flags(reset_flags)
        '''

    # Carica settings all’avvio
    with SETTINGS_FILE.open("r", encoding="utf-8-sig") as f:
        settings = json.load(f)
    
    # =====================================================
    # Controllo disponibilità TTS (aggiornato con JSON e colori)
    # =====================================================
    tts_status = check_tts_status()

    if tts_status["tts_available"]:
        # Messaggio in verde dal JSON o da Messages
        print(Fore.GREEN + "\n---------------------------------------" + Style.RESET_ALL)
        print(Fore.GREEN + messages.RegistaTTSActive + Style.RESET_ALL)
        print(Fore.GREEN + messages.RegistaTTSProviders, tts_status["active_providers"])
        print(Fore.GREEN + "---------------------------------------" + Style.RESET_ALL)
        tts_enabled = True
    else:
        # Messaggio in giallo o rosso dal JSON o da Messages
        print(Fore.YELLOW + messages.RegistaTTSDisabled + Style.RESET_ALL)
        #if tts_status["missing_info"][0]:
         #   print(Fore.YELLOW + tts_status["missing_info"][0] + " → " + str(tts_status["missing_info"][1]) + Style.RESET_ALL)
        tts_enabled = False

    logger.info("Regista", "main", "Application started",
                context={"tts_available": tts_enabled,
                         "providers": tts_status.get("active_providers", [])})

    # =====================================================
    # Verifica aggiornamenti
    # =====================================================
    _GIST_URL = "https://gist.githubusercontent.com/SmallSoftwareHouse/48337de1f302edb88bf952ddf51c2755/raw/version.json"
    _SETTINGS_DEFAULT = Path.cwd() / "Settings" / "settings_default.json"
    try:
        with _SETTINGS_DEFAULT.open("r", encoding="utf-8") as _f:
            _current_version = str(json.load(_f).get("version", "0.1"))
    except Exception:
        _current_version = "0.1"

    _update_available, _available_version = check_for_updates(_current_version, _GIST_URL)
    if _update_available is True:
        print(Fore.CYAN + f"\n{'=' * 60}" + Style.RESET_ALL)
        print(Fore.CYAN + messages.update_checker_available_title + Style.RESET_ALL)
        print(Fore.CYAN + messages.update_checker_available_msg.format(
            current=_current_version, available=_available_version) + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)
        logger.info("Regista", "main", "Update available",
                    context={"current_version": _current_version,
                             "available_version": _available_version,
                             "gist_url": _GIST_URL})
    elif _update_available is False:
        logger.info("Regista", "main", "Application is up to date",
                    context={"current_version": _current_version})
    else:
        logger.warning("Regista", "main", messages.update_checker_failed,
                       context={"current_version": _current_version})

    # =====================================================
    # Main loop
    # =====================================================
    ws = WorkspaceManager.get_active()
    if ws is not None:
        msg = getattr(messages, "RegistaLoadedProject", "Progetto caricato: {0}").format(ws.name)
        print(Fore.GREEN + msg + Style.RESET_ALL)

    while True:
        if ws is None:
            ws = seleziona_o_crea_progetto(messages, settings)

        mostra_titolo_menu(messages, "MenuFlussoLavoroTitle", ws, width=54)
        mostra_info_workspace(ws, messages)
        scelta = menu(messages, tts_enabled)

        if scelta is not None:
            logger.info("Regista", "main", f"Menu option selected: {scelta}")

        if scelta == '0':
            ws = gestione_progetti(messages, ws, settings)
            print_separator(5)
        elif scelta == '1':
            estrai_tracce(messages, settings)
            print_separator(5)
        elif scelta == '2':
            trascrivi_audio(messages, settings)
            print_separator(5)
        elif scelta == '3':
            traduci_testo(messages, settings)
            print_separator(5)
        elif scelta == '4':
            if tts_enabled:
                from tts_menu import tts_menu
                tts_menu(messages, settings)
                print_separator(5)
            else:
                print(Fore.YELLOW + messages.RegistaMenuOption4Disabled + Style.RESET_ALL)
        elif scelta == '8':
            new_messages = settings_manager.main(messages)
            if new_messages is not None:
                messages = new_messages
            with SETTINGS_FILE.open("r", encoding="utf-8-sig") as f:
                settings = json.load(f)
            print_separator(5)
        elif scelta is not None and scelta.lower() == 'r':
            send_error_report(logger, messages)
            print_separator(5)
        elif scelta is not None and scelta.lower() == 'x':
            # Check for errors before exit and prompt to report
            if has_errors(logger):
                prompt = getattr(messages, "RegistaExitErrorsPrompt",
                                 "Questa sessione contiene errori. Inviare una segnalazione? (s/n):")
                answer = input(Fore.YELLOW + prompt + " " + Style.RESET_ALL).strip()
                if is_yes(answer, messages):
                    send_error_report(logger, messages)
            print(messages.RegistaExit)
            logger.info("Regista", "main", "User exited application")
            break
        else:
            if scelta is not None:
                print(messages.RegistaChoiceInvalid)


# =========================================================
# Entry point - Load messages and start main loop
# =========================================================
# =========================================================
# Windows console close handler (X button / logoff / shutdown)
# =========================================================
def _register_console_close_handler():
    """
    Register a Windows console control handler so that closing the window
    with X (or system logoff/shutdown) triggers a clean session close and
    creates a silent ZIP report before the process is terminated.
    Does nothing on non-Windows platforms.
    """
    import sys
    if sys.platform != "win32":
        return
    try:
        import ctypes
        import ctypes.wintypes

        CTRL_CLOSE_EVENT    = 2
        CTRL_LOGOFF_EVENT   = 5
        CTRL_SHUTDOWN_EVENT = 6

        HandlerRoutine = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.DWORD)

        def _handler(ctrl_type):
            if ctrl_type in (CTRL_CLOSE_EVENT, CTRL_LOGOFF_EVENT, CTRL_SHUTDOWN_EVENT):
                # Close session as window-closed (writes session_end + exit_reason)
                logger.close_session(exit_reason="window_closed")
                # Create ZIP silently — no user interaction needed/possible
                create_silent_exit_report(logger)
            return False  # let Windows proceed with default termination

        # Keep a reference so the callback isn't garbage-collected
        _register_console_close_handler._ctypes_handler = HandlerRoutine(_handler)
        ctypes.windll.kernel32.SetConsoleCtrlHandler(
            _register_console_close_handler._ctypes_handler, True
        )
    except Exception:
        pass  # non-critical — app still works without it


if __name__ == "__main__":
    _register_console_close_handler()
    messages = Messages()
    try:
        main(messages)
    finally:
        logger.close_session()


# estrai_tracce.py

import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from colorama import Fore, Style
import logging
import secrets
import traceback as _tb_module
from core.logger import logger

# =========================================================
# InfoManager integration
# =========================================================
from info_manager import InfoManager
from core.messages import Messages
from core.workspace_manager import WorkspaceManager
from core.utils_settings import write_json_atomic
from core.archive_pruner import prune_with_confirmation
from core.source_importer import ask_import
from core.ui_printer import offer_open_folder
from pathlib import Path

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
messages = Messages(locale_folder=Path(BASE_DIR) / "locale" / "Active")

# =========================================================
# Function to display submenu titles
# =========================================================
def mostra_titolo_menu(messages, titolo_key):
    C, R = Fore.CYAN, Style.RESET_ALL
    titolo = getattr(messages, titolo_key, getattr(messages, "MISSING_KEY", "[STRINGA MANCANTE]"))
    print(C + '-'*28 + R)
    print(C + titolo + R)
    print(C + '-'*28 + R)


# =========================================================
# VIDEO FILE SELECTION
# =========================================================
def seleziona_file_video(messages, VIDEO_DIR):
    while True:
        print()
        mostra_titolo_menu(messages, "MenuEstrazioneTracceTitle")

        files = [f for f in os.listdir(VIDEO_DIR)
                 if f.lower().endswith(('.mp4', '.mkv', '.mov'))]

        if files:
            print(messages.ESTR_select_menu_option_1)
        else:
            print(Style.DIM + f"{messages.ESTR_select_menu_option_1}  {messages.MENU_folder_empty}" + Style.RESET_ALL)
        print(messages.ESTR_select_menu_option_2)
        print(messages.ESTR_select_menu_option_0)

        scelta = input(messages.ESTR_select_choice).strip()

        if scelta == '0':
            print(Fore.YELLOW + messages.ESTR_operation_cancelled + Style.RESET_ALL)
            return None

        elif scelta == '1':
            if not files:
                print(Fore.YELLOW + messages.ESTR_no_files_in_folder + Style.RESET_ALL)
                print(Fore.YELLOW + messages.ESTR_folder_empty_browse_hint + Style.RESET_ALL)
                continue

            for i, f in enumerate(files, start=1):
                print(f"{i}. {f}")

            idx = input(messages.ESTR_select_index).strip()
            if not idx.isdigit():
                print(Fore.RED + messages.ESTR_invalid_index + Style.RESET_ALL)
                continue

            idx = int(idx)
            if idx < 1 or idx > len(files):
                print(Fore.RED + messages.ESTR_invalid_index + Style.RESET_ALL)
                continue

            return os.path.join(VIDEO_DIR, files[idx - 1])

        elif scelta == '2':
            desktop = Path.home() / "Desktop"
            default_dir = desktop if desktop.exists() else Path.home()
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title=messages.ESTR_file_dialog_title,
                initialdir=str(default_dir),
                filetypes=[("Video files", "*.mp4 *.mkv *.mov")]
            )

            if not file_path:
                print(Fore.YELLOW + messages.ESTR_no_file_selected + Style.RESET_ALL)
                continue

            return file_path

        else:
            print(Fore.RED + messages.ESTR_choice_invalid + Style.RESET_ALL)


# =========================================================
# Count audio tracks
# =========================================================
def conta_tracce_audio(ffprobe_path, video_path):
    cmd = [
        ffprobe_path,
        '-v', 'error',
        '-select_streams', 'a',
        '-show_entries', 'stream=index',
        '-of', 'csv=p=0'
    ]
    result = subprocess.run(cmd + [video_path], capture_output=True, text=True)
    if result.returncode != 0:
        return 0
    lines = result.stdout.strip().split('\n')
    return len([l for l in lines if l.strip()])


# =========================================================
# AUDIO TRACK EXTRACTION
# =========================================================
def estrai_tracce(messages, settings):
    _t0 = datetime.now()
    video_file = None
    n_tracce = 0
    logger.info("estrai_tracce", "estrai_tracce", "Audio extraction started")

    # =========================================================
    # 1) Resolve workspace paths
    # =========================================================
    ws = WorkspaceManager.get_active()
    VIDEO_DIR = ws.root / "video_input"
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    # =========================================================
    # 2) Select video file (with import dialog for external files)
    # =========================================================
    video_file = None
    source_mode = "external"
    while True:
        raw_path = seleziona_file_video(messages, VIDEO_DIR)
        if not raw_path:
            return
        final_path, source_mode = ask_import(raw_path, VIDEO_DIR, messages)
        if final_path is not None:
            video_file = str(final_path)
            break
        # user cancelled import — loop back to file selection
    print()

    # =========================================================
    # 3) Video name and FFmpeg/FFprobe paths
    # =========================================================
    video_name = os.path.splitext(os.path.basename(video_file))[0]

    FFMPEG_PATH  = os.path.join(BASE_DIR, 'Tools', 'ffmpeg-7.1.1-full_build', 'bin', 'ffmpeg.exe')
    FFPROBE_PATH = os.path.join(BASE_DIR, 'Tools', 'ffmpeg-7.1.1-full_build', 'bin', 'ffprobe.exe')

    # =========================================================
    # 4) Initialize InfoManager at workspace root
    # =========================================================
    info_manager = InfoManager(ws.root)

    info_manager.update_project(
        nome_progetto=video_name,
        settings=settings,
        note=""
    )
    info_manager.analyze_video(video_file, FFPROBE_PATH, source_mode=source_mode)

    # Reset track list before (re-)extraction
    info_manager.data["audio_tracce"] = []

    # =========================================================
    # 5) Count audio tracks
    # =========================================================
    n_tracce = conta_tracce_audio(FFPROBE_PATH, video_file)
    print(Fore.CYAN + f"{messages.ESTR_audio_tracks_found} {n_tracce}" + Style.RESET_ALL)

    if n_tracce == 0:
        print(Fore.YELLOW + messages.ESTR_no_audio_tracks + Style.RESET_ALL)
        return

    # =========================================================
    # 6) Extract audio tracks — all in audio_extraction/current/
    # =========================================================
    print(messages.ESTR_extracting_tracks)
    extracted_tracks = []

    # Archive previous extraction (if any), then prune old archives
    extraction_dir = ws.root / "audio_extraction"
    current_dir = extraction_dir / "current"
    archive_dir = extraction_dir / "archive"

    if current_dir.exists():
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        suffix    = secrets.token_hex(2)
        dest      = archive_dir / f"{timestamp}_{suffix}"
        archive_dir.mkdir(parents=True, exist_ok=True)
        current_dir.rename(dest)

    current_dir.mkdir(parents=True, exist_ok=True)

    for i in range(n_tracce):
        track_id   = f"track_{i+1:02d}"
        wav_filename = f"{track_id}.wav"
        output_path  = current_dir / wav_filename

        cmd_audio = [
            FFMPEG_PATH,
            '-y',
            '-i', video_file,
            '-map', f'0:a:{i}',
            '-c:a', 'pcm_s16le',
            str(output_path)
        ]

        try:
            subprocess.run(cmd_audio, capture_output=True, text=True, check=True)
            print(Fore.GREEN + f"{messages.ESTR_track_saved} {output_path}" + Style.RESET_ALL)

            # Add to InfoManager (uses ffprobe to get audio properties)
            info_manager.add_audio_track(str(output_path), ffprobe_path=FFPROBE_PATH, track_id=track_id)

            # Write per-track metadata.json with track_XX prefix
            track_data = info_manager.data["audio_tracce"][-1]
            write_json_atomic(current_dir / f"{track_id}_metadata.json", {
                "schema_version": 1,
                "track_id":    track_id,
                "created_at":  datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "source_file": os.path.basename(video_file),
                "stream_index": i,
                "codec":       track_data.get("codec"),
                "sample_rate": track_data.get("sample_rate_hz"),
                "channels":    track_data.get("canali"),
                "bit_depth":   track_data.get("bit_depth"),
                "duration_s":  track_data.get("durata_s"),
                "size_mb":     track_data.get("dimensione_MB"),
            })

            extracted_tracks.append(track_id)

        except subprocess.CalledProcessError as e:
            logging.warning(messages.INFO_Error_FFProbe.format(path=output_path, errore=e.stderr))
            logger.error("estrai_tracce", "estrai_tracce",
                         messages.INFO_Error_FFProbe.format(path=str(output_path), errore=e.stderr),
                         error_code="EXTRACTION_FFMPEG_ERROR", error_category="SYSTEM",
                         is_retryable=True, traceback=_tb_module.format_exc())
            print(Fore.YELLOW + f"{messages.ESTR_track_error} {i+1}" + Style.RESET_ALL)

    # =========================================================
    # 7) Finalize InfoManager
    # =========================================================
    info_manager.set_audio_track_count(n_tracce)

    try:
        info_manager.generate_info_file(messages)
        print(Fore.GREEN + f"{messages.ESTR_reference_file_created} {info_manager.info_path}" + Style.RESET_ALL)
    except Exception as e:
        logging.warning(messages.INFO_Error_WritingInfo.format(path=info_manager.info_path, errore=e))
        logger.error("estrai_tracce", "estrai_tracce",
                     messages.INFO_Error_WritingInfo.format(path=str(info_manager.info_path), errore=e),
                     error_code="EXTRACTION_INFO_WRITE_ERROR", error_category="FILE",
                     is_retryable=False, traceback=_tb_module.format_exc())
        print(Fore.RED + f"{messages.ESTR_reference_file_failed} {e}" + Style.RESET_ALL)

    _dur = round((datetime.now() - _t0).total_seconds() * 1000)
    logger.operation("estrai_tracce", "estrai_tracce", "Audio extraction completed",
                     status="SUCCESS", duration_ms=_dur,
                     context={"video": os.path.basename(video_file) if video_file else None,
                              "tracks": n_tracce,
                              "extracted": extracted_tracks,
                              "workspace": ws.name})

    offer_open_folder(ws.root / "audio_extraction" / "current", messages)


# =========================================================
# SELF-TEST
# =========================================================
if __name__ == "__main__":
    import json

    with open(os.path.join(BASE_DIR, 'locale', 'Active', 'it.json'), encoding='utf-8') as f:
        messages_data = json.load(f)

    class Messages:
        def __getattr__(self, item):
            return messages_data.get(item, f"[MISSING: {item}]")

    estrai_tracce(Messages())
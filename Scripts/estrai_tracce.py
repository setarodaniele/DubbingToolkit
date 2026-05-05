# estrai_tracce.py

import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from colorama import Fore, Style
from backup_utils import manage_history
import logging
import traceback as _tb_module
from core.logger import logger

# =========================================================
# InfoManager integration
# =========================================================
from info_manager import InfoManager
from core.messages import Messages
from pathlib import Path

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
messages = Messages(locale_folder=Path(BASE_DIR) / "locale" / "Active")

# =========================================================
# Function to display submenu titles
# =========================================================
def mostra_titolo_menu(messages, titolo_key):
    titolo = getattr(messages, titolo_key, getattr(messages, "MISSING_KEY", "[STRINGA MANCANTE]"))
    print(Fore.CYAN + '-'*28)
    print(titolo)
    print('-'*28 + Style.RESET_ALL)


# =========================================================
# VIDEO FILE SELECTION
# =========================================================
def seleziona_file_video(messages, VIDEO_DIR):
    print()
    mostra_titolo_menu(messages, "MenuEstrazioneTracceTitle")

    print(messages.ESTR_select_menu_option_1)
    print(messages.ESTR_select_menu_option_2)
    print(messages.ESTR_select_menu_option_0)

    scelta = input(messages.ESTR_select_choice).strip()

    if scelta == '0':
        print(Fore.YELLOW + messages.ESTR_operation_cancelled + Style.RESET_ALL)
        return None

    elif scelta == '1':
        files = [f for f in os.listdir(VIDEO_DIR)
                 if f.lower().endswith(('.mp4', '.mkv', '.mov'))]

        if not files:
            print(Fore.RED + messages.ESTR_no_files_in_folder + Style.RESET_ALL)
            return None

        for i, f in enumerate(files, start=1):
            print(f"{i}. {f}")

        idx = input(messages.ESTR_select_index).strip()
        if not idx.isdigit():
            print(Fore.RED + messages.ESTR_invalid_index + Style.RESET_ALL)
            return None

        idx = int(idx)
        if idx < 1 or idx > len(files):
            print(Fore.RED + messages.ESTR_invalid_index + Style.RESET_ALL)
            return None

        return os.path.join(VIDEO_DIR, files[idx - 1])

    elif scelta == '2':
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title=messages.ESTR_file_dialog_title,
            initialdir=VIDEO_DIR,
            filetypes=[("Video files", "*.mp4 *.mkv *.mov")]
        )

        if not file_path:
            print(Fore.YELLOW + messages.ESTR_no_file_selected + Style.RESET_ALL)
            return None

        return file_path

    else:
        print(Fore.RED + messages.ESTR_choice_invalid + Style.RESET_ALL)
        return None


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
    # 1) Define base directories
    VIDEO_DIR = os.path.join(BASE_DIR, 'Video_Input')
    AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, 'Audio_Extracted')
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

    # =========================================================
    # 2) Select video file
    video_file = seleziona_file_video(messages, VIDEO_DIR)
    if not video_file:
        return
    print()

    # =========================================================
    # 3) Extract video name and create timestamp
    video_name = os.path.splitext(os.path.basename(video_file))[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # =========================================================
    # 4) Create extraction directory
    extraction_dir = os.path.join(AUDIO_OUTPUT_DIR, f"{timestamp}_{video_name}")
    os.makedirs(extraction_dir, exist_ok=True)

    # =========================================================
    # 5) Define paths to FFmpeg and FFprobe
    # =========================================================
    FFMPEG_PATH = os.path.join(BASE_DIR, 'Tools', 'ffmpeg-7.1.1-full_build', 'bin', 'ffmpeg.exe')
    FFPROBE_PATH = os.path.join(BASE_DIR, 'Tools', 'ffmpeg-7.1.1-full_build', 'bin', 'ffprobe.exe')

    # =========================================================
    # 6) Initialize InfoManager and update project
    # =========================================================
    info_manager = InfoManager(extraction_dir)

    # Update project section in JSON
    info_manager.update_project(
        nome_progetto=video_name,
        settings=settings,
        note=""
    )

    # Analyze video and populate video_file section
    info_manager.analyze_video(video_file, FFPROBE_PATH)

    # =========================================================
    # 7) Count audio tracks
    # =========================================================
    n_tracce = conta_tracce_audio(FFPROBE_PATH, video_file)
    print(Fore.CYAN + f"{messages.ESTR_audio_tracks_found} {n_tracce}" + Style.RESET_ALL)

    if n_tracce == 0:
        print(Fore.YELLOW + messages.ESTR_no_audio_tracks + Style.RESET_ALL)
        return

    # =========================================================
    # 8) Extract audio tracks and add to InfoManager
    # =========================================================
    print(messages.ESTR_extracting_tracks)
    for i in range(n_tracce):
        track_name = f"Track{i+1}_{video_name}.wav"
        output_path = os.path.join(extraction_dir, track_name)

        cmd_audio = [
            FFMPEG_PATH,
            '-y',                  # overwrite if exists
            '-i', video_file,      # source video
            '-map', f'0:a:{i}',    # select the i-th audio track
            '-c:a', 'pcm_s16le',   # WAV codec
            output_path
        ]

        try:
            subprocess.run(cmd_audio, capture_output=True, text=True, check=True)
            print(Fore.GREEN + f"{messages.ESTR_track_saved} {output_path}" + Style.RESET_ALL)

            # Add audio track metadata to JSON
            info_manager.add_audio_track(output_path, ffprobe_path=FFPROBE_PATH)

        except subprocess.CalledProcessError as e:
            logging.warning(messages.INFO_Error_FFProbe.format(path=output_path, errore=e.stderr))
            logger.error("estrai_tracce", "estrai_tracce",
                         messages.INFO_Error_FFProbe.format(path=output_path, errore=e.stderr),
                         error_code="EXTRACTION_FFMPEG_ERROR", error_category="SYSTEM",
                         is_retryable=True, traceback=_tb_module.format_exc())
            print(Fore.YELLOW + f"{messages.ESTR_track_error} {i+1}" + Style.RESET_ALL)

    # =========================================================
    # 9) Update the number of audio tracks in video_file section
    # =========================================================
    info_manager.set_audio_track_count(n_tracce)

    # =========================================================
    # 10) Generate human-readable info file
    # =========================================================
    try:
        info_manager.generate_info_file(messages)
        print(Fore.GREEN + f"{messages.ESTR_reference_file_created} {info_manager.info_path}" + Style.RESET_ALL)
    except Exception as e:
        logging.warning(messages.INFO_Error_WritingInfo.format(path=info_manager.info_path, errore=e))
        logger.error("estrai_tracce", "estrai_tracce",
                     messages.INFO_Error_WritingInfo.format(path=info_manager.info_path, errore=e),
                     error_code="EXTRACTION_INFO_WRITE_ERROR", error_category="FILE",
                     is_retryable=False, traceback=_tb_module.format_exc())
        print(Fore.RED + f"{messages.ESTR_reference_file_failed} {e}" + Style.RESET_ALL)

    # =========================================================
    # 11) Manage extraction history
    # =========================================================
    manage_history(AUDIO_OUTPUT_DIR, settings, messages)

    _dur = round((datetime.now() - _t0).total_seconds() * 1000)
    logger.operation("estrai_tracce", "estrai_tracce", "Audio extraction completed",
                     status="SUCCESS", duration_ms=_dur,
                     context={"video": os.path.basename(video_file) if video_file else None,
                              "tracks": n_tracce,
                              "output_dir": os.path.basename(extraction_dir)})


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
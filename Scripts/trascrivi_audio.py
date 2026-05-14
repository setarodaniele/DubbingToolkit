# =========================================================
# trascrivi_audio.py
# =========================================================

from SilenziaWarning import *  # suppress warnings
import whisper
import os
import traceback as _tb_module
from colorama import Fore, Style
import json
from datetime import datetime, timedelta
from core.logger import logger
import tkinter as tk
from tkinter import filedialog
import torch
from menu_lingue import seleziona_lingua
from pydub import AudioSegment, silence
from segmentazione_avanzata import create_pause_based_srt
from info_manager import InfoManager
from pathlib import Path

from core.workspace_manager import WorkspaceManager
from core.utils_settings import write_json_atomic
from core.archive_pruner import prune_with_confirmation, prune_by_language
from core.source_importer import ask_import
from core.ui_printer import offer_open_folder


# =========================================================
# 1) HELPER FUNCTIONS
# =========================================================

def mostra_titolo_menu(messages, title_key):
    C, R = Fore.CYAN, Style.RESET_ALL
    title = getattr(messages, title_key, "[MISSING TITLE]")
    print()
    print(C + '-' * 28 + R)
    print(C + title + R)
    print(C + '-' * 28 + R)


def selezione_file_manuale(messages, initial_dir=None):
    if initial_dir is None:
        desktop = Path.home() / "Desktop"
        initial_dir = str(desktop) if desktop.exists() else str(Path.home())
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title=messages.TRANSCR_file_dialog_title,
        initialdir=initial_dir,
        filetypes=[("Audio files", "*.wav *.mp3")]
    )
    if not file_path:
        print(Fore.YELLOW + messages.TRANSCR_no_file_selected + Style.RESET_ALL)
        return None
    return Path(file_path)


def _next_track_id(ws):
    """Return the next available track_XX id for the transcripts stage."""
    transcripts_dir = ws.root / "transcripts"
    if not transcripts_dir.exists():
        return "track_01"
    existing = sorted(
        d.name for d in transcripts_dir.iterdir()
        if d.is_dir() and d.name.startswith("track_")
    )
    if not existing:
        return "track_01"
    try:
        n = int(existing[-1].split("_")[1]) + 1
    except (IndexError, ValueError):
        n = len(existing) + 1
    return f"track_{n:02d}"


def _collect_extracted_tracks(extraction_dir):
    """Return list of (track_id, Path) from audio_extraction/current/track_XX.wav."""
    tracks = []
    current = extraction_dir / "current"
    if not current.exists():
        return tracks
    for file_path in sorted(current.glob("track_*.wav")) + sorted(current.glob("track_*.mp3")):
        if file_path.is_file():
            track_id = file_path.stem
            tracks.append((track_id, file_path))
    return tracks


def _collect_input_files(audio_input_dir):
    """Return sorted list of audio Paths from audio_input/."""
    if not audio_input_dir.exists():
        return []
    return sorted(
        f for f in audio_input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in ('.wav', '.mp3')
    )


def _print_folder_option(num, label, has_content, empty_label):
    """Print a menu option, dimmed with empty_label when folder is empty."""
    if has_content:
        print(f"  {num}. {label}")
    else:
        print(Style.DIM + f"  {num}. {label}  {empty_label}" + Style.RESET_ALL)


def _submenu_files(messages, title, items, format_fn):
    """Show a numbered sub-menu of files; return selected index (0-based) or None (back)."""
    while True:
        print()
        print(Fore.CYAN + "-" * 28)
        print(title)
        print("-" * 28 + Style.RESET_ALL)
        for i, item in enumerate(items, 1):
            print(f"  {i}. {format_fn(item)}")
        print(f"  0. {messages.MENU_option_back}")
        choice = input(messages.TRANSCR_select_folder_prompt).strip()
        if not choice.isdigit():
            print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)
            continue
        choice = int(choice)
        if choice == 0:
            return None
        if 1 <= choice <= len(items):
            return choice - 1
        print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)


def seleziona_file_audio(messages, ws):
    """Select an audio file from the workspace.

    Returns (track_id, Path) or None if the user cancels.
    Audio from audio_extraction keeps its track_id.
    Audio from audio_input or manual selection gets the next available id.
    """
    extraction_dir = ws.root / "audio_extraction"
    audio_input_dir = ws.root / "audio_input"

    while True:
        tracks = _collect_extracted_tracks(extraction_dir)
        input_files = _collect_input_files(audio_input_dir)

        mostra_titolo_menu(messages, "TRANSCR_menu_title")
        _print_folder_option("1", messages.TRANSCR_option_audio_extracted, tracks, messages.MENU_folder_empty)
        _print_folder_option("2", messages.TRANSCR_option_audio_input, input_files, messages.MENU_folder_empty)
        print(f"  3. {messages.TRANSCR_select_audio_manual}")
        print(f"  0. {messages.TRANSCR_select_audio_cancel}")

        choice = input(messages.TRANSCR_select_folder_prompt).strip()

        if choice == "0":
            return None
        elif choice == "1":
            if not tracks:
                print(Fore.YELLOW + f"{messages.TRANSCR_option_audio_extracted}: {messages.MENU_folder_empty}" + Style.RESET_ALL)
                continue
            idx = _submenu_files(messages, messages.TRANSCR_submenu_audio_extracted,
                                  tracks, lambda t: f"[{t[0]}] {t[1].name}")
            if idx is not None:
                track_id, fpath = tracks[idx]
                print(Fore.GREEN + messages.TRANSCR_file_selected.format(file=str(fpath)) + Style.RESET_ALL)
                return (track_id, fpath)
        elif choice == "2":
            if not input_files:
                print(Fore.YELLOW + f"{messages.TRANSCR_option_audio_input}: {messages.MENU_folder_empty}" + Style.RESET_ALL)
                continue
            idx = _submenu_files(messages, messages.TRANSCR_submenu_audio_input,
                                  input_files, lambda f: f.name)
            if idx is not None:
                fpath = input_files[idx]
                print(Fore.GREEN + messages.TRANSCR_file_selected.format(file=str(fpath)) + Style.RESET_ALL)
                return (_next_track_id(ws), fpath)
        elif choice == "3":
            initial = str(extraction_dir) if tracks else str(audio_input_dir)
            fpath = selezione_file_manuale(messages, initial_dir=initial)
            if fpath:
                final_path, _ = ask_import(fpath, audio_input_dir, messages)
                if final_path is None:
                    continue  # user cancelled import — loop back to menu
                return (_next_track_id(ws), final_path)
        else:
            print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)


def seleziona_modello_whisper(messages):
    print(messages.TRANSCR_WhisperPrompt)
    models = ["tiny", "base", "small", "medium", "large"]
    for i, m in enumerate(models, start=1):
        print(f"{i}. {m}")
    print("0. " + messages.TRANSCR_select_audio_cancel)
    while True:
        choice = input(messages.TRANSCR_select_model_prompt + " (default: small): ").strip()
        if not choice:
            return "small"
        if not choice.isdigit():
            print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)
            continue
        choice = int(choice)
        if choice == 0:
            return None
        elif 1 <= choice <= len(models):
            return models[choice - 1]
        else:
            print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)


def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def save_srt(transcription_segments, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, segment in enumerate(transcription_segments, start=1):
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            text = segment['text'].strip()
            f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")


def mostra_valutazione_lingua(detected_lang, probability, messages):
    perc = int(probability * 100)
    lang_name = getattr(messages, f"LANG_{detected_lang}", detected_lang)
    if perc >= 95:
        desc = messages.TRANSCR_lang_confidence_excellent
    elif perc >= 75:
        desc = messages.TRANSCR_lang_confidence_good
    elif perc >= 50:
        desc = messages.TRANSCR_lang_confidence_average
    elif perc >= 25:
        desc = messages.TRANSCR_lang_confidence_poor
    else:
        desc = messages.TRANSCR_lang_confidence_very_poor
    bar_length = 6
    filled_length = int(bar_length * perc / 100)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    print(Fore.CYAN + "-" * 40 + Style.RESET_ALL)
    print(Fore.CYAN + f"{messages.TRANSCR_lang_detected}: {lang_name.capitalize()}")
    print(f"{messages.TRANSCR_lang_certainty}: {perc}%" + Style.RESET_ALL)
    print(Fore.CYAN + "-" * 40 + Style.RESET_ALL)
    print(messages.TRANSCR_lang_quick_eval)
    print(f"100% {'█' * 6} {messages.TRANSCR_lang_confidence_excellent}")
    print(f"90%  {'█' * 5} {messages.TRANSCR_lang_confidence_good}")
    print(f"75%  {'█' * 4} {messages.TRANSCR_lang_confidence_average}")
    print(f"50%  {'█' * 3} {messages.TRANSCR_lang_confidence_poor}")
    print(f"25%  {'█' * 2} {messages.TRANSCR_lang_confidence_very_poor}")
    print()


# =========================================================
# 2) MAIN WORKFLOW
# =========================================================

def trascrivi_audio(messages, settings):
    _t0 = datetime.now()
    logger.info("trascrivi_audio", "trascrivi_audio", "Transcription started")

    # 2.1) Resolve workspace paths
    ws = WorkspaceManager.get_active()

    # 2.2) Select audio file
    selection = seleziona_file_audio(messages, ws)
    if not selection:
        return
    track_id, audio_file = selection
    print()

    # 2.3) Set transcription language from settings
    selected_lang = settings.get("Transcript_Audio_Spoken_Lang", "it")
    print(Fore.CYAN + messages.TRANSCR_lang_selected_from_settings.format(lang=selected_lang) + Style.RESET_ALL)

    # 2.4) Select Whisper model
    model_choice = seleziona_modello_whisper(messages)
    if not model_choice:
        return
    print(Fore.CYAN + messages.TRANSCR_loading_model.format(model=model_choice) + Style.RESET_ALL)

    # 2.5) Set processing device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(Fore.CYAN + messages.TRANSCR_processing_device.format(device=device.upper()) + Style.RESET_ALL)
    _model_t0 = datetime.now()
    model = whisper.load_model(model_choice, device=device)
    logger.operation("trascrivi_audio", "trascrivi_audio", "Whisper model loaded",
                     status="SUCCESS",
                     duration_ms=round((datetime.now() - _model_t0).total_seconds() * 1000),
                     context={"model": model_choice, "device": device})

    # 2.6) Load and preprocess audio
    print(Fore.CYAN + messages.TRANSCR_language_analysis.format(file=str(audio_file)) + Style.RESET_ALL)
    audio = whisper.load_audio(str(audio_file))
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # 2.7) Detect language
    _, probs = model.detect_language(mel)
    detected_lang = max(probs, key=probs.get)
    lang_prob = probs[detected_lang]
    mostra_valutazione_lingua(detected_lang, lang_prob, messages)

    # 2.8) Compare selected vs detected language
    if selected_lang == detected_lang:
        lang_name = getattr(messages, f"LANG_{detected_lang}", detected_lang)
        print(Fore.CYAN + messages.TRANSCR_lang_match.format(lang=lang_name) + Style.RESET_ALL)
    else:
        detected_name = getattr(messages, f"LANG_{detected_lang}", detected_lang)
        selected_name = getattr(messages, f"LANG_{selected_lang}", selected_lang)
        print(Fore.YELLOW + messages.TRANSCR_lang_mismatch_alert.format(
            manual=selected_name, detected=detected_name) + Style.RESET_ALL)
        confirm_prompt = f"{messages.TRANSCR_confirm_transcription_prompt} ({messages.YES_SHORT}/{messages.NO_SHORT}): "
        confirm = input(Fore.YELLOW + confirm_prompt + Style.RESET_ALL).strip().lower()
        if not confirm:
            confirm = messages.YES_SHORT.lower()
        if confirm not in [messages.YES_SHORT.lower(), messages.YES_FULL.lower()]:
            print(Fore.YELLOW + messages.TRANSCR_transcription_cancelled + Style.RESET_ALL)
            logger.info("trascrivi_audio", "trascrivi_audio", "Transcription cancelled by user",
                        context={"reason": "language_mismatch_rejected",
                                 "selected_lang": selected_lang, "detected_lang": detected_lang})
            return

    # 2.9) Prepare output directory
    audio_filename = audio_file.stem
    ws.rotate_to_archive("transcripts", track_id)
    prune_with_confirmation(
        ws, "transcripts", track_id, messages,
        show_confirmations=settings.get("show_confirmations", True),
        use_trash=settings.get("use_trash", False),
        max_count=settings.get("max_backups", 10),
    )
    prune_by_language(
        ws, "transcripts", track_id,
        lang_key="detected_lang",
        max_per_lang=settings.get("max_backups_per_language", 10),
        use_trash=settings.get("use_trash", False),
    )
    transcript_dir = ws.stage_current("transcripts", track_id)
    transcript_dir.mkdir(parents=True, exist_ok=True)

    # 2.10) Transcribe audio (RAW segments)
    print(Fore.CYAN + messages.TRANSCR_transcribing_raw.format(file=str(audio_file)) + Style.RESET_ALL)
    _transcr_t0 = datetime.now()
    try:
        result_raw = model.transcribe(str(audio_file), language=selected_lang, task="transcribe")
    except Exception as e:
        _tb_module.print_exc()
        logger.error("trascrivi_audio", "trascrivi_audio", str(e),
                     error_code="TRANSCRIPTION_WHISPER_FAILED", error_category="SYSTEM",
                     is_retryable=True, traceback=_tb_module.format_exc())
        return
    logger.operation("trascrivi_audio", "trascrivi_audio", "Whisper transcription completed",
                     status="SUCCESS",
                     duration_ms=round((datetime.now() - _transcr_t0).total_seconds() * 1000),
                     context={"audio_file": audio_file.name,
                              "language": selected_lang, "detected_lang": detected_lang,
                              "segments": len(result_raw["segments"])})

    # =========================================================
    # 2.11) Save RAW transcription SRT
    # =========================================================
    srt_raw_path = transcript_dir / f"{audio_filename}_{detected_lang}_raw.srt"
    save_srt(result_raw['segments'], srt_raw_path)
    print(Fore.GREEN + messages.TRANSCR_transcription_saved_raw.format(file=str(srt_raw_path)) + Style.RESET_ALL)

    # =========================================================
    # 2.11b) Ask if user wants segmented transcription
    # =========================================================
    # Segmentazione avanzata disattivata (temporaneamente)
    segmentation_enabled = False
    print(Fore.CYAN + messages.TRANSCR_segmented_disabled + Style.RESET_ALL)

    # =========================================================
    # 2.12) Segmented transcription (optional)
    # =========================================================
    if segmentation_enabled:
        srt_seg_path = transcript_dir / f"{audio_filename}_{detected_lang}_seg.srt"

        create_pause_based_srt(
            audio_file=str(audio_file),
            output_srt_path=str(srt_seg_path),
            model=model,
            language=selected_lang,
            min_silence_len=settings.get("MIN_SILENCE_LEN_MS", 1200),
            silence_thresh=settings.get("SILENCE_THRESH_DBFS", -30),
            keep_silence=settings.get("KEEP_SILENCE_MS", 150),
            messages=messages
        )

        print(Fore.GREEN + messages.TRANSCR_transcription_saved_seg.format(file=str(srt_seg_path)) + Style.RESET_ALL)

    else:
        srt_seg_path = None

    # =========================================================
    # 2.13) Create WORK SRT for manual editing
    # =========================================================
    import shutil

    srt_work_path = transcript_dir / f"{audio_filename}_{detected_lang}_work.srt"

    if segmentation_enabled:
        shutil.copyfile(srt_seg_path, srt_work_path)
    else:
        shutil.copyfile(srt_raw_path, srt_work_path)

    print(Fore.GREEN + messages.TRANSCR_transcription_saved_work.format(file=str(srt_work_path)) + Style.RESET_ALL)

    # =========================================================
    # 2.14) Write per-track metadata
    # =========================================================
    audio_segment_obj = AudioSegment.from_file(str(audio_file))
    audio_duration = round(len(audio_segment_obj) / 1000, 2)

    _created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_json_atomic(transcript_dir / "metadata.json", {
        "schema_version": 1,
        "track_id":             track_id,
        "created_at":           _created_at,
        "source_audio":         audio_file.name,
        "spoken_lang":          selected_lang,
        "detected_lang":        detected_lang,
        "lang_probability":     round(lang_prob, 3),
        "whisper_model":        model_choice,
        "device":               device,
        "audio_duration_s":     audio_duration,
        "segments_count":       len(result_raw["segments"]),
        "segmentation_enabled": segmentation_enabled,
        "srt_raw":              srt_raw_path.name,
        "srt_work":             srt_work_path.name,
        "srt_seg":              srt_seg_path.name if srt_seg_path else None,
    })

    try:
        InfoManager(ws.root).update_trascrizione(track_id, {
            "created_at":       _created_at,
            "whisper_model":    model_choice,
            "spoken_lang":      selected_lang,
            "detected_lang":    detected_lang,
            "lang_probability": round(lang_prob, 3),
            "audio_duration_s": audio_duration,
            "segments_count":   len(result_raw["segments"]),
        })
    except Exception:
        pass

    _dur = round((datetime.now() - _t0).total_seconds() * 1000)
    logger.operation("trascrivi_audio", "trascrivi_audio", "Transcription session finished",
                     status="SUCCESS", duration_ms=_dur,
                     context={"audio_file": audio_file.name,
                              "track_id": track_id,
                              "model": model_choice, "language": selected_lang,
                              "detected_lang": detected_lang,
                              "lang_probability": round(lang_prob, 3),
                              "workspace": ws.name})

    offer_open_folder(transcript_dir, messages)


# =========================================================
# 3) MAIN
# =========================================================
if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # 3.1) Load settings
    SETTINGS_FILE = os.path.join(BASE_DIR, 'Settings', 'settings.json')
    with open(SETTINGS_FILE, encoding='utf-8-sig') as f:
        settings = json.load(f)

    # 3.2) Load locale
    LOCALE_FILE = os.path.join(BASE_DIR, 'locale', 'Active', f"{settings.get('interface_lang', 'it')}.json")
    with open(LOCALE_FILE, encoding='utf-8-sig') as f:
        messages_data = json.load(f)

    class Messages:
        def __getattr__(self, item):
            return messages_data.get(item, f"[MISSING: {item}]")
    messages = Messages()

    # 3.3) Start transcription
    trascrivi_audio(messages, settings)

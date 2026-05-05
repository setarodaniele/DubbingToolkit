# =========================================================
# trascrivi_audio.py - versione con InfoManager
# =========================================================

from SilenziaWarning import *  # suppress warnings
import whisper
import os
import traceback as _tb_module
from colorama import Fore, Style
import json
from backup_utils import manage_history
from datetime import datetime, timedelta
from core.logger import logger
import tkinter as tk
from tkinter import filedialog
import torch
from menu_lingue import seleziona_lingua
from pydub import AudioSegment, silence
from segmentazione_avanzata import create_pause_based_srt
from info_manager import InfoManager  # <- use InfoManager for info file handling


# =========================================================
# 1) HELPER FUNCTIONS
# =========================================================

def mostra_titolo_menu(messages, title_key):
    title = getattr(messages, title_key, "[MISSING TITLE]")
    print()
    print(Fore.CYAN + '-' * 28)
    print(title)
    print('-' * 28 + Style.RESET_ALL)


def selezione_file_manuale(messages, initial_dir=None):
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
    return file_path


def seleziona_file_audio(messages, AUDIO_DIR, INPUT_DIR):
    folders = [f for f in os.listdir(AUDIO_DIR) if os.path.isdir(os.path.join(AUDIO_DIR, f))]
    folders.sort(reverse=True)
    print(messages.TRANSCR_select_extraction_folder)
    for i, folder in enumerate(folders, start=1):
        print(f"{i}. {folder}")
    manual_option_index = len(folders) + 1
    print(f"{manual_option_index}. {messages.TRANSCR_select_audio_manual}")
    print(f"0. {messages.TRANSCR_select_audio_cancel}")
    while True:
        choice = input(messages.TRANSCR_select_folder_prompt).strip()
        if not choice.isdigit():
            print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)
            continue
        choice = int(choice)
        if choice == 0:
            return None
        elif 1 <= choice <= len(folders):
            selected_folder = os.path.join(AUDIO_DIR, folders[choice - 1])
        elif choice == manual_option_index:
            return selezione_file_manuale(messages, initial_dir=AUDIO_DIR)
        else:
            print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)
            continue
        break
    files = [f for f in os.listdir(selected_folder) if f.lower().endswith(('.wav', '.mp3'))]
    files.sort()
    if not files:
        print(messages.TRANSCR_no_audio_files_in_folder.format(folder=os.path.basename(selected_folder)))
        return None
    print(messages.TRANSCR_select_audio_in_folder.format(folder=os.path.basename(selected_folder)))
    for i, f in enumerate(files, start=1):
        print(f"{i}. {f}")
    print(f"0. {messages.TRANSCR_select_audio_cancel}")
    while True:
        choice = input(messages.TRANSCR_select_audio_prompt).strip()
        if not choice.isdigit():
            print(Fore.RED + messages.TRANSCR_invalid_choice + Style.RESET_ALL)
            continue
        choice = int(choice)
        if choice == 0:
            return None
        elif 1 <= choice <= len(files):
            selected_file = os.path.join(selected_folder, files[choice - 1])
            print(Fore.GREEN + messages.TRANSCR_file_selected.format(file=selected_file) + Style.RESET_ALL)
            return selected_file
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

'''
def conta_blocchi_e_caratteri(srt_file):
    blocchi = 0
    tot_caratteri = 0
    with open(srt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.isdigit():  # inizia un blocco
            blocchi += 1
            i += 2  # salto numero e timestamp
            testo = ""
            while i < len(lines) and lines[i].strip() != "":
                testo += lines[i].strip()
                i += 1
            tot_caratteri += len(testo)
        else:
            i += 1
    return blocchi, tot_caratteri'''

        
# =========================================================
# 2) MAIN WORKFLOW
# =========================================================

def trascrivi_audio(messages, settings):
    _t0 = datetime.now()
    logger.info("trascrivi_audio", "trascrivi_audio", "Transcription started")

    # 2.1) Define base directories
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    AUDIO_DIR = os.path.join(BASE_DIR, 'Audio_Extracted')
    INPUT_DIR = os.path.join(BASE_DIR, 'Audio_Input')
    TRANSCRIPTS_DIR = os.path.join(BASE_DIR, settings.get("output_transcripts", "Transcripts"))

    # 2.2) Show menu title
    mostra_titolo_menu(messages, "TRANSCR_menu_title")

    # 2.3) Select audio file
    audio_file = seleziona_file_audio(messages, AUDIO_DIR, INPUT_DIR)
    if not audio_file:
        return       

    # 2.4) Set transcription language from settings
    selected_lang = settings.get("Transcript_Audio_Spoken_Lang", "it")
    print(Fore.CYAN + messages.TRANSCR_lang_selected_from_settings.format(lang=selected_lang) + Style.RESET_ALL)

    # 2.5) Select Whisper model
    model_choice = seleziona_modello_whisper(messages)
    if not model_choice:
        return
    print(Fore.CYAN + messages.TRANSCR_loading_model.format(model=model_choice) + Style.RESET_ALL)

    # 2.6) Set processing device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(Fore.CYAN + messages.TRANSCR_processing_device.format(device=device.upper()) + Style.RESET_ALL)
    _model_t0 = datetime.now()
    model = whisper.load_model(model_choice, device=device)
    logger.operation("trascrivi_audio", "trascrivi_audio", "Whisper model loaded",
                     status="SUCCESS",
                     duration_ms=round((datetime.now() - _model_t0).total_seconds() * 1000),
                     context={"model": model_choice, "device": device})

    # 2.7) Load and preprocess audio
    print(Fore.CYAN + messages.TRANSCR_language_analysis.format(file=audio_file) + Style.RESET_ALL)
    audio = whisper.load_audio(audio_file)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # 2.8) Detect language
    _, probs = model.detect_language(mel)
    detected_lang = max(probs, key=probs.get)
    lang_prob = probs[detected_lang]
    mostra_valutazione_lingua(detected_lang, lang_prob, messages)

    # 2.9) Compare selected vs detected language
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

    # 2.10) Create transcript folder
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    audio_filename = os.path.splitext(os.path.basename(audio_file))[0]
    transcript_dir = os.path.join(TRANSCRIPTS_DIR, f"{timestamp}_{detected_lang}_{audio_filename}")
    os.makedirs(transcript_dir, exist_ok=True)

    # 2.11) Transcribe audio (RAW segments)
    print(Fore.CYAN + messages.TRANSCR_transcribing_raw.format(file=audio_file) + Style.RESET_ALL)
    _transcr_t0 = datetime.now()
    try:
        result_raw = model.transcribe(audio_file, language=selected_lang, task="transcribe")
    except Exception as e:
        _tb_module.print_exc()
        logger.error("trascrivi_audio", "trascrivi_audio", str(e),
                     error_code="TRANSCRIPTION_WHISPER_FAILED", error_category="SYSTEM",
                     is_retryable=True, traceback=_tb_module.format_exc())
        return
    logger.operation("trascrivi_audio", "trascrivi_audio", "Whisper transcription completed",
                     status="SUCCESS",
                     duration_ms=round((datetime.now() - _transcr_t0).total_seconds() * 1000),
                     context={"audio_file": os.path.basename(audio_file),
                              "language": selected_lang, "detected_lang": detected_lang,
                              "segments": len(result_raw["segments"])})

    # =========================================================
    # 2.12) Save RAW transcription SRT
    # =========================================================
    srt_raw_path = os.path.join(transcript_dir, f"{audio_filename}_{detected_lang}_raw.srt")
    save_srt(result_raw['segments'], srt_raw_path)
    print(Fore.GREEN + messages.TRANSCR_transcription_saved_raw.format(file=srt_raw_path) + Style.RESET_ALL)

    # =========================================================
    # 2.12b) Ask if user wants segmented transcription
    # =========================================================
    # Segmentazione avanzata disattivata (temporaneamente)
    segmentation_enabled = False
    print(Fore.CYAN + messages.TRANSCR_segmented_disabled + Style.RESET_ALL)
    '''
    segmentation_enabled = True

    prompt_msg = (
        messages.TRANSCR_segmented_optional_warning + "\n"
        + f"({messages.YES_SHORT}/{messages.NO_SHORT}, default: {messages.NO_SHORT}): "
    )

    choice = input(Fore.YELLOW + prompt_msg + Style.RESET_ALL).strip().lower()

    if choice not in [messages.YES_SHORT.lower(), messages.YES_FULL.lower()]:
        segmentation_enabled = False
        print(Fore.CYAN + messages.TRANSCR_segmented_skipped + Style.RESET_ALL)
    '''
    
    # =========================================================
    # 2.13) Segmented transcription (optional)
    # =========================================================
    if segmentation_enabled:

        srt_seg_path = os.path.join(transcript_dir, f"{audio_filename}_{detected_lang}_seg.srt")

        create_pause_based_srt(
            audio_file=audio_file,
            output_srt_path=srt_seg_path,
            model=model,
            language=selected_lang,
            min_silence_len=settings.get("MIN_SILENCE_LEN_MS", 1200),
            silence_thresh=settings.get("SILENCE_THRESH_DBFS", -30),
            keep_silence=settings.get("KEEP_SILENCE_MS", 150),
            messages=messages
        )

        print(Fore.GREEN + messages.TRANSCR_transcription_saved_seg.format(file=srt_seg_path) + Style.RESET_ALL)

    else:
        srt_seg_path = None

    # =========================================================
    # 2.14) Create WORK SRT for manual editing
    # =========================================================
    import shutil

    srt_work_path = os.path.join(transcript_dir, f"{audio_filename}_{detected_lang}_work.srt")

    if segmentation_enabled:
        shutil.copyfile(srt_seg_path, srt_work_path)
    else:
        shutil.copyfile(srt_raw_path, srt_work_path)

    print(Fore.GREEN + messages.TRANSCR_transcription_saved_work.format(file=srt_work_path) + Style.RESET_ALL)
    
        
    # 2.15) Setup segments
    transcription_segments = result_raw['segments']
    transcription_segments_raw = result_raw['segments']
    transcription_segments_work = transcription_segments

    # 2.16) Manage transcript history
    manage_history(TRANSCRIPTS_DIR, settings, messages)

    # =========================================================
    # 2.17) Aggiorna JSON con InfoManager in modo sicuro
    # =========================================================

    # Calcolo durata audio
    audio_segment = AudioSegment.from_file(audio_file)
    audio_duration = round(len(audio_segment) / 1000, 2)

    # JSON della fase precedente (estrazione tracce)
    source_json = os.path.join(
        BASE_DIR,
        "Audio_Extracted",
        os.path.basename(os.path.dirname(audio_file)),
        "project_info.json"
    )

    # Carica InfoManager sulla cartella trascrizione
    info_manager = InfoManager(
        transcript_dir,
        current_section="trascrizione",
        source_json=source_json
    )

    # Aggiorna la sezione "trascrizione"
    info_manager.update_trascrizione(
        audio_file=audio_file,
        selected_lang=selected_lang,
        audio_duration=audio_duration,
        model_choice=model_choice,
        device=device,
        detected_lang=detected_lang,
        lang_prob=lang_prob,
        segmentation_enabled=segmentation_enabled,
        srt_raw_path=srt_raw_path,
        srt_seg_path=srt_seg_path,
        srt_work_path=srt_work_path,
        messages=messages
    )

    _dur = round((datetime.now() - _t0).total_seconds() * 1000)
    logger.operation("trascrivi_audio", "trascrivi_audio", "Transcription session finished",
                     status="SUCCESS", duration_ms=_dur,
                     context={"audio_file": os.path.basename(audio_file),
                              "model": model_choice, "language": selected_lang,
                              "detected_lang": detected_lang,
                              "lang_probability": round(lang_prob, 3)})

    
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
# =========================================================
# segmentazione_avanzata.py
# Advanced pause-based segmentation with Whisper re-transcription
# =========================================================

from pydub import AudioSegment, silence
from datetime import timedelta
import numpy as np
from colorama import Fore, Style

# =========================================================
# 1) TIME & SRT UTILITIES
# =========================================================

def format_timestamp(seconds: float) -> str:
    """
    1.1) Convert seconds to SRT timestamp (HH:MM:SS,mmm)
    """
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def save_srt(segments: list, output_path: str):
    """
    1.2) Save segments list to SRT file
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, start=1):
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg.get("text", "").strip()
            f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")


# =========================================================
# 2) AUDIO SEGMENTATION (SILENCE-BASED)
# =========================================================

def split_audio_on_silence(
    audio_path: str,
    min_silence_len: int,
    silence_thresh: int,
    keep_silence: int
) -> list:
    """
    2.1) Detect non-silent segments based on pauses
    Returns a list of dicts with start/end in seconds
    """
    audio = AudioSegment.from_file(audio_path)

    nonsilent_ranges = silence.detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        seek_step=1
    )

    segments = []
    for start_ms, end_ms in nonsilent_ranges:
        start_sec = max((start_ms - keep_silence) / 1000.0, 0)
        end_sec = min((end_ms + keep_silence) / 1000.0, audio.duration_seconds)

        segments.append({
            "start": start_sec,
            "end": end_sec,
            "text": ""
        })

    return segments


# =========================================================
# 3) AUDIO CONVERSION FOR WHISPER
# =========================================================

def audiosegment_to_float32_mono(audio_seg: AudioSegment) -> np.ndarray:
    """
    3.1) Convert AudioSegment to float32 mono @ 16kHz for Whisper
    """
    audio_seg = audio_seg.set_channels(1).set_frame_rate(16000)
    samples = np.array(audio_seg.get_array_of_samples()).astype(np.float32)
    samples /= 32768.0
    return samples


# =========================================================
# 4) SEGMENT TRANSCRIPTION WITH PRELOADED MODEL
# =========================================================

def transcribe_segments_with_model(
    audio_file: str,
    segments: list,
    model,
    language: str
) -> list:
    """
    4.1) Transcribe each segment using a preloaded Whisper model
    """
    audio_full = AudioSegment.from_file(audio_file)

    for seg in segments:
        start_ms = int(seg["start"] * 1000)
        end_ms = int(seg["end"] * 1000)

        # filtro minimo durata segmento
       # if (seg["end"] - seg["start"]) < 0.8:
        #    continue

        segment_audio = audio_full[start_ms:end_ms]

        # filtro sicurezza audio troppo corto
       # if len(segment_audio) < 200:
       #     continue

        audio_np = audiosegment_to_float32_mono(segment_audio)

        result = model.transcribe(
            audio_np,
            language=language,
            task="transcribe"
        )

        text = result["text"].strip()

        # filtro output vuoto
        if not text:
            continue

        seg["text"] = text

    return segments


# =========================================================
# 5) MAIN FUNCTION – ADVANCED SEGMENTATION
# =========================================================

def create_pause_based_srt(
    audio_file: str,
    output_srt_path: str,
    model,
    language: str,
    min_silence_len: int,
    silence_thresh: int,
    keep_silence: int,
    messages
) -> list:
    """
    5.1) Full advanced segmentation pipeline:
         - silence-based segmentation
         - Whisper re-transcription per segment
         - final SRT generation
    """

    # --- 5.2) Detect pause-based segments
    print(Fore.CYAN + "[Segmentazione Avanzata] Detecting pauses..." + Style.RESET_ALL)

    segments = split_audio_on_silence(
        audio_path=audio_file,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence
    )

    # --- 5.3) Transcribe each segment
    print(Fore.CYAN + "[Segmentazione Avanzata] Transcribing segments..." + Style.RESET_ALL)

    segments = transcribe_segments_with_model(
        audio_file=audio_file,
        segments=segments,
        model=model,
        language=language
    )

    # --- 5.4) Save final SRT
    save_srt(segments, output_srt_path)
    return segments

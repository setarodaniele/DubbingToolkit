# =========================================================
# info_manager.py
# =========================================================
# Manages project_info.json at the workspace root.
# Covers extraction phase: project metadata, video info, audio tracks.
# Per-stage transcription/translation/TTS data lives in per-track metadata.json files.
# =========================================================

import os
import json
from datetime import datetime
from pathlib import Path
import wave
import contextlib
import subprocess
import logging

from core.messages import Messages
from core.utils_settings import write_json_atomic

logging.basicConfig(level=logging.WARNING, format='[%(levelname)s] %(message)s')

try:
    import mutagen
except ImportError:
    mutagen = None


# =========================================================
# InfoManager class
# =========================================================
class InfoManager:

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.json_path = self.base_dir / "project_info.json"
        self.info_path = self.base_dir / "project_info.txt"
        self.data = self._load_or_init()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_or_init(self):
        default_structure = {
            "schema_version": 1,
            "progetto": {},
            "video_file": {},
            "audio_tracce": [],
            "trascrizione": {},
            "traduzioni": {},
            "TTS": {},
            "storico_rinomina": [],
        }

        if self.json_path.exists():
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for key, default_value in default_structure.items():
                    if key not in data:
                        data[key] = default_value
                return data
            except Exception as e:
                msg = Messages().INFO_Error_LoadingJSON.format(path=self.json_path, errore=e)
                logging.warning(msg)

        return default_structure

    def _to_relative(self, path) -> str:
        """Return forward-slash relative path if inside base_dir, else absolute string."""
        try:
            return Path(path).resolve().relative_to(self.base_dir.resolve()).as_posix()
        except ValueError:
            return str(Path(path).resolve())

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_json(self):
        if "progetto" in self.data:
            self.data["progetto"]["ultima_modifica"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            write_json_atomic(self.json_path, self.data)
        except Exception as e:
            msg = Messages().INFO_Error_SavingJSON.format(path=self.json_path, errore=e)
            logging.warning(msg)

    # ------------------------------------------------------------------
    # Project section
    # ------------------------------------------------------------------

    def update_project(self, nome_progetto, settings, note=""):
        if "data_creazione" not in self.data["progetto"]:
            self.data["progetto"]["data_creazione"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.data["progetto"].update({
            "nome_progetto": nome_progetto,
            "interface_lang": settings.get("interface_lang"),
            "Transcript_Audio_Spoken_Lang": settings.get("Transcript_Audio_Spoken_Lang"),
            "Transcript_Target_Lang": settings.get("Transcript_Target_Lang"),
            "Translation_Target_Lang": settings.get("Translation_Target_Lang"),
            "Dubbing_Lang": settings.get("Dubbing_Lang"),
            "note": note
        })

        self.data["progetto"]["ultima_modifica"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_json()

    def record_rename(self, old_name: str, new_name: str):
        """Append a rename entry to storico_rinomina and save."""
        if "storico_rinomina" not in self.data:
            self.data["storico_rinomina"] = []
        self.data["storico_rinomina"].append({
            "da": old_name,
            "a": new_name,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        self.save_json()

    # ------------------------------------------------------------------
    # Video file section
    # ------------------------------------------------------------------

    def update_video_file(self, path, durata_s=None, codec_video=None, frame_rate=None, risoluzione=None, source_mode=None):
        path_resolved = str(Path(path).resolve())
        dimensione_MB = os.path.getsize(path) / (1024 * 1024) if os.path.exists(path) else 0

        self.data["video_file"].update({
            "file_sorgente": path_resolved,
            "dimensione_MB": dimensione_MB,
            "durata_s": durata_s,
            "codec_video": codec_video,
            "frame_rate": frame_rate,
            "risoluzione": risoluzione,
        })
        if source_mode is not None:
            self.data["video_file"]["source_mode"] = source_mode

        self.save_json()

    # ------------------------------------------------------------------
    # Audio tracks
    # ------------------------------------------------------------------

    def add_audio_track(self, path, ffprobe_path=None, track_id=None):
        """Append audio track data to audio_tracce[].

        Paths inside the workspace are stored as forward-slash relative strings.
        track_id is derived from the path if not passed explicitly.
        """
        abs_path = str(Path(path).resolve())
        rel_path = self._to_relative(path)

        # Derive track_id from path
        if track_id is None:
            # Try old structure: audio_extraction/track_XX/current/...
            candidate = Path(path).parent.parent.name
            if candidate.startswith("track_"):
                track_id = candidate
            else:
                # Try new structure: audio_extraction/current/track_XX.wav
                file_stem = Path(path).stem
                if file_stem.startswith("track_"):
                    track_id = file_stem

        durata_s = 0
        sample_rate_hz = 0
        channels = 0
        bit_depth = 0
        codec = "Unknown"
        dimensione_MB = os.path.getsize(abs_path) / (1024 * 1024) if os.path.exists(abs_path) else 0

        try:
            with contextlib.closing(wave.open(abs_path, 'r')) as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                durata_s = frames / float(rate)
                sample_rate_hz = rate
                channels = wf.getnchannels()
                bit_depth = wf.getsampwidth() * 8
        except Exception as e:
            msg = Messages().INFO_Error_ReadingWAV.format(path=abs_path, errore=e)
            logging.warning(msg)
            if mutagen:
                try:
                    audio_file = mutagen.File(abs_path)
                    if audio_file:
                        durata_s = audio_file.info.length
                        sample_rate_hz = getattr(audio_file.info, 'sample_rate', 0)
                        channels = getattr(audio_file.info, 'channels', 0)
                        bit_depth = 0
                except Exception as e2:
                    msg2 = Messages().INFO_Error_ReadingAudio.format(path=abs_path, errore=e2)
                    logging.warning(msg2)

        if ffprobe_path and Path(ffprobe_path).exists():
            try:
                cmd = [
                    str(ffprobe_path), '-v', 'error',
                    '-select_streams', 'a:0',
                    '-show_entries', 'stream=codec_name',
                    '-of', 'default=nw=1:nk=1',
                    abs_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                codec = result.stdout.strip() or codec
            except Exception as e:
                msg = Messages().INFO_Error_FFProbe.format(path=abs_path, errore=e)
                logging.warning(msg)

        self.data["audio_tracce"].append({
            "track_id":         track_id,
            "nome_file":        Path(abs_path).name,
            "file_destinazione": rel_path,
            "durata_s":         durata_s,
            "canali":           channels,
            "sample_rate_hz":   sample_rate_hz,
            "bit_depth":        bit_depth,
            "codec":            codec,
            "dimensione_MB":    dimensione_MB
        })
        self.save_json()

    def set_audio_track_count(self, count):
        if "video_file" not in self.data:
            self.data["video_file"] = {}
        self.data["video_file"]["audio_tracce"] = count
        self.save_json()

    # ------------------------------------------------------------------
    # Video analysis
    # ------------------------------------------------------------------

    def analyze_video(self, video_path, ffprobe_path=None, source_mode=None):
        video_path = str(Path(video_path).resolve())
        if not Path(video_path).exists():
            logging.warning(f"Video not found: {video_path}")
            return

        durata_s = None
        codec_video = None
        frame_rate = None
        risoluzione = None

        if ffprobe_path and Path(ffprobe_path).exists():
            try:
                cmd_duration = [ffprobe_path, '-v', 'error', '-show_entries',
                                'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
                result = subprocess.run(cmd_duration, capture_output=True, text=True)
                durata_s = float(result.stdout.strip()) if result.stdout.strip() else None

                cmd_stream = [ffprobe_path, '-v', 'error', '-select_streams', 'v:0',
                              '-show_entries', 'stream=codec_name,width,height,r_frame_rate',
                              '-of', 'default=noprint_wrappers=1', video_path]
                result = subprocess.run(cmd_stream, capture_output=True, text=True)
                width = None
                for line in result.stdout.strip().splitlines():
                    if line.startswith("codec_name="):
                        codec_video = line.split('=')[1]
                    elif line.startswith("width="):
                        width = int(line.split('=')[1])
                    elif line.startswith("height="):
                        height = int(line.split('=')[1])
                        if width is not None:
                            risoluzione = f"{width}x{height}"
                    elif line.startswith("r_frame_rate="):
                        fr = line.split('=')[1]
                        if '/' in fr:
                            num, denom = fr.split('/')
                            frame_rate = round(float(num) / float(denom), 2) if float(denom) != 0 else None
            except Exception as e:
                logging.warning(f"Error analyzing video {video_path}: {e}")

        self.update_video_file(
            path=video_path,
            durata_s=durata_s,
            codec_video=codec_video,
            frame_rate=frame_rate,
            risoluzione=risoluzione,
            source_mode=source_mode,
        )

    # ------------------------------------------------------------------
    # Per-stage pipeline sections (keyed by track_id)
    # ------------------------------------------------------------------

    def _update_track_section(self, section: str, track_id: str, data: dict):
        """Write or overwrite a track entry within a named top-level section."""
        if not isinstance(self.data.get(section), dict):
            self.data[section] = {}
        self.data[section][track_id] = data
        if "progetto" in self.data:
            self.data["progetto"]["ultima_modifica"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_json()

    def update_trascrizione(self, track_id: str, data: dict):
        self._update_track_section("trascrizione", track_id, data)

    def update_traduzione(self, track_id: str, data: dict):
        self._update_track_section("traduzioni", track_id, data)

    def update_tts(self, track_id: str, data: dict):
        self._update_track_section("TTS", track_id, data)

    # ------------------------------------------------------------------
    # Generic section update
    # ------------------------------------------------------------------

    def update_section_with_merge(self, section_name, new_data, merge=True):
        if section_name not in self.data or not isinstance(self.data[section_name], dict):
            self.data[section_name] = {}
        if merge:
            self.data[section_name].update(new_data)
        else:
            self.data[section_name] = new_data
        if "progetto" in self.data:
            self.data["progetto"]["ultima_modifica"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_json()

    # ------------------------------------------------------------------
    # Human-readable info file
    # ------------------------------------------------------------------

    def generate_info_file(self, messages):
        lines = []

        def lang_human_readable(code):
            if not code:
                return ""
            return f"{getattr(messages, f'LANG_{code}', code)} ({code})"

        lines.append(getattr(messages, "INFO_Progetto"))
        for k, v in self.data["progetto"].items():
            label = getattr(messages, f"INFO_Progetto_{k}", k)
            if k in ["interface_lang", "Transcript_Audio_Spoken_Lang", "Transcript_Target_Lang",
                     "Translation_Target_Lang", "Dubbing_Lang"]:
                v = lang_human_readable(v)
            lines.append(f"{label}: {v}")

        lines.append("\n" + getattr(messages, "INFO_Video"))
        for k, v in self.data["video_file"].items():
            label = getattr(messages, f"INFO_Video_{k}", k)
            lines.append(f"{label}: {v:.2f}" if isinstance(v, float) else f"{label}: {v}")

        lines.append("\n" + getattr(messages, "INFO_Audio"))
        for idx, t in enumerate(self.data["audio_tracce"], start=1):
            lines.append(f"{getattr(messages, 'INFO_Audio_Traccia').format(idx)}:")
            for k, v in t.items():
                label = getattr(messages, f"INFO_Audio_{k}", k)
                lines.append(f"  {label}: {v:.2f}" if isinstance(v, float) else f"  {label}: {v}")

        for section_key, header_key, header_default in [
            ("trascrizione", "INFO_Trascrizione", "=== TRASCRIZIONE ==="),
            ("traduzioni",   "INFO_Traduzioni",   "=== TRADUZIONI ==="),
            ("TTS",          "INFO_TTSDoppiaggio", "=== DOPPIAGGIO TTS ==="),
        ]:
            section = self.data.get(section_key, {})
            if section:
                lines.append("\n" + getattr(messages, header_key, header_default))
                for tid, tdata in section.items():
                    lines.append(f"  {tid}:")
                    for k, v in tdata.items():
                        label = getattr(messages, f"{header_key}_{k}", k)
                        lines.append(f"    {label}: {v:.2f}" if isinstance(v, float) else f"    {label}: {v}")

        renames = self.data.get("storico_rinomina", [])
        if renames:
            lines.append("\n" + getattr(messages, "INFO_StoricRinomina", "=== RENAME HISTORY ==="))
            tmpl = getattr(messages, "INFO_StoricRinomina_entry", "{data}: {da} → {a}")
            for entry in renames:
                lines.append(tmpl.format(**entry))

        with open(self.info_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

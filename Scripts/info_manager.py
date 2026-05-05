# =========================================================
# info_manager.py
# =========================================================
# Centralized management of info files and JSON for each project
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

# -------------------------
# Logging configuration
# -------------------------
logging.basicConfig(level=logging.WARNING, format='[%(levelname)s] %(message)s')

# -------------------------
# Optional mutagen for non-WAV audio
# -------------------------
try:
    import mutagen
except ImportError:
    mutagen = None

# =========================================================
# 1) InfoManager class
# =========================================================
class InfoManager:
    # =========================================================
    # 1.1) Constructor
    # =========================================================
    def __init__(self, base_dir, current_section=None, source_json=None):
        self.base_dir = Path(base_dir)
        self.json_path = self.base_dir / "project_info.json"
        self.info_path = self.base_dir / "project_info.txt"

        self.current_section = current_section
        self.source_json = source_json

        self.data = self._load_or_init()

        # eredita automaticamente se necessario
        if current_section and source_json:
            self._inherit_previous()

    # =========================================================
    # 1.2) Load JSON or initialize default structure
    # =========================================================
    def _load_or_init(self):
        default_structure = {
            "progetto": {},
            "video_file": {},
            "audio_tracce": [],
            "trascrizione": {},
            "traduzioni": {},
            "TTS": {}
        }

        if self.json_path.exists():
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # ensure all keys exist
                for key, default_value in default_structure.items():
                    if key not in data:
                        data[key] = default_value

                return data

            except Exception as e:
                msg = Messages().INFO_Error_LoadingJSON.format(path=self.json_path, errore=e)
                logging.warning(msg)

        return default_structure

    # =========================================================
    # 1.3) Save JSON data to disk
    # =========================================================
    def save_json(self):
        if "progetto" in self.data:
            self.data["progetto"]["ultima_modifica"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            msg = Messages().INFO_Error_SavingJSON.format(path=self.json_path, errore=e)
            logging.warning(msg)

    # =========================================================
    # 2) Update project section with settings
    # =========================================================
    def update_project(self, nome_progetto, settings, note=""):
        """
        Update the project section using the JSON settings.
        Uses exact key names from settings to avoid renaming.
        """
        # 2.1) Set creation date if not already present
        if "data_creazione" not in self.data["progetto"]:
            self.data["progetto"]["data_creazione"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2.2) Retrieve languages directly from settings
        interface_lang = settings.get("interface_lang", None)
        Transcript_Audio_Spoken_Lang = settings.get("Transcript_Audio_Spoken_Lang", None)
        Transcript_Target_Lang = settings.get("Transcript_Target_Lang", None)
        Translation_Target_Lang = settings.get("Translation_Target_Lang", None)
        Dubbing_Lang = settings.get("Dubbing_Lang", None)

        # 2.3) Update project JSON
        self.data["progetto"].update({
            "nome_progetto": nome_progetto,
            "interface_lang": interface_lang,
            "Transcript_Audio_Spoken_Lang": Transcript_Audio_Spoken_Lang,
            "Transcript_Target_Lang": Transcript_Target_Lang,
            "Translation_Target_Lang": Translation_Target_Lang,
            "Dubbing_Lang": Dubbing_Lang,
            "note": note
        })

        # 2.4) Update last modification and save
        self.data["progetto"]["ultima_modifica"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_json()

    # =========================================================
    # 3) Update video file section
    # =========================================================
    def update_video_file(self, path, durata_s=None, codec_video=None, frame_rate=None, risoluzione=None):
        path_resolved = str(Path(path).resolve())
        dimensione_MB = os.path.getsize(path) / (1024 * 1024) if os.path.exists(path) else 0

        self.data["video_file"].update({
            "file_sorgente": path_resolved,
            "dimensione_MB": dimensione_MB,
            "durata_s": durata_s,
            "codec_video": codec_video,
            "frame_rate": frame_rate,
            "risoluzione": risoluzione
        })

        self.save_json()

    # =========================================================
    # 4) Add audio track
    # =========================================================
    def add_audio_track(self, path, ffprobe_path=None):
        path = str(Path(path).resolve())
        durata_s = 0
        sample_rate_hz = 0
        channels = 0
        bit_depth = 0
        codec = "Unknown"
        dimensione_MB = os.path.getsize(path) / (1024 * 1024) if os.path.exists(path) else 0

        # 4.1) Read WAV properties
        try:
            with contextlib.closing(wave.open(path,'r')) as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                durata_s = frames / float(rate)
                sample_rate_hz = rate
                channels = wf.getnchannels()
                bit_depth = wf.getsampwidth() * 8
        except Exception as e:
            msg = Messages().INFO_Error_ReadingWAV.format(path=path, errore=e)
            logging.warning(msg)
            if mutagen:
                try:
                    audio_file = mutagen.File(path)
                    if audio_file:
                        durata_s = audio_file.info.length
                        sample_rate_hz = getattr(audio_file.info, 'sample_rate', 0)
                        channels = getattr(audio_file.info, 'channels', 0)
                        bit_depth = 0
                except Exception as e2:
                    msg2 = Messages().INFO_Error_ReadingAudio.format(path=path, errore=e2)
                    logging.warning(msg2)

        # 4.2) Get codec via ffprobe if available
        if ffprobe_path and Path(ffprobe_path).exists():
            try:
                cmd = [
                    str(ffprobe_path),
                    '-v', 'error',
                    '-select_streams', 'a:0',
                    '-show_entries', 'stream=codec_name',
                    '-of', 'default=nw=1:nk=1',
                    path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                codec = result.stdout.strip() or codec
            except Exception as e:
                msg = Messages().INFO_Error_FFProbe.format(path=path, errore=e)
                logging.warning(msg)

        # 4.3) Append track to JSON
        self.data["audio_tracce"].append({
            "nome_file": Path(path).name,
            "file_destinazione": path,
            "durata_s": durata_s,
            "canali": channels,
            "sample_rate_hz": sample_rate_hz,
            "bit_depth": bit_depth,
            "codec": codec,
            "dimensione_MB": dimensione_MB
        })
        self.save_json()

    # =========================================================
    # 5) Update transcription (versione aggiornata)
    # =========================================================
    def update_trascrizione(
        self,
        audio_file,
        selected_lang,
        detected_lang,
        lang_prob,
        audio_duration,
        model_choice,
        device,       
        segmentation_enabled,
        srt_raw_path,
        srt_seg_path=None,
        srt_work_path=None,
        messages=None
    ):
        self.update_section_with_merge("trascrizione", {
            "audio_file": audio_file,
            "selected_lang": selected_lang,
            "detected_lang": detected_lang,
            "lang_prob": lang_prob,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "audio_duration": audio_duration,
            "model_choice": model_choice,
            "device": device,                     
            "segmentation_enabled": segmentation_enabled,
            "files": {
                "raw": self.analizza_file_srt(srt_raw_path, messages.INFO_Fallback_RAW),
                "segmented": self.analizza_file_srt(srt_seg_path, messages.INFO_Fallback_SEGMENTED),
                "work": self.analizza_file_srt(srt_work_path, messages.INFO_Fallback_WORK)
            }
        }, merge=True)

        # Aggiorna ultima modifica
        if "progetto" in self.data:
            self.data["progetto"]["ultima_modifica"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_json()

        if messages:
            self.generate_info_file(messages)

    # =========================================================
    # 6) Update translation
    # =========================================================
    def update_traduzione(
        self,
        source_file,
        target_file,
        source_lang,
        target_lang,
        translation_model,
        messages=None
    ):
        """
        Aggiorna la sezione 'traduzioni' nel JSON con:
        - Percorso file sorgente e tradotto
        - Lingue
        - Modello usato
        - Timestamp
        - Conteggio blocchi e caratteri dal file tradotto
        - Eventuali avvisi (frasi non tradotte)
        """
        # Analizza SRT tradotto
        srt_data = self.analizza_file_srt(target_file, file_not_present_label="File tradotto mancante")

        # Opzionale: rileva linee vuote o frasi non tradotte
        warnings = []
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith("[UNTRANSLATED]"):  # convenzione ipotetica
                        warnings.append(line)
        except Exception:
            pass

        # Aggiorna sezione traduzioni
        self.update_section_with_merge("traduzioni", {
            "source_file": str(source_file),
            "translated_file": str(target_file),
            "source_lang": source_lang,
            "target_lang": target_lang,
            "translation_model": translation_model,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "numero_blocchi": srt_data.get("numero_blocchi", 0),
            "tot_caratteri": srt_data.get("tot_caratteri", 0),
            "warnings": warnings
        }, merge=True)

        # Aggiorna info file se richiesto
        if messages:
            self.generate_info_file(messages)
            
            
        # =========================================================
        # 7) Update TTS
        # =========================================================
        def update_tts(self, motore, caratteri_usati, percentuale_franchigia=None, costo_stimato_euro=None):
            self.data["TTS"][motore] = {
                "caratteri_usati": caratteri_usati,
                "percentuale_franchigia": percentuale_franchigia,
                "costo_stimato_euro": costo_stimato_euro
            }
            self.save_json()

    # =========================================================
    # 8) Generate readable info file
    # =========================================================
    def generate_info_file(self, messages):
        lines = []

        # Helper: convert language code to human-readable
        def lang_human_readable(code):
            if not code:
                return ""
            return f"{getattr(messages, f'LANG_{code}', code)} ({code})"

        # 8.1) PROJECT
        lines.append(getattr(messages, "INFO_Progetto"))
        for k, v in self.data["progetto"].items():
            label = getattr(messages, f"INFO_Progetto_{k}", k)
            # If the key is a language field, convert to human-readable
            if k in ["interface_lang", "Transcript_Audio_Spoken_Lang", "Transcript_Target_Lang",
                     "Translation_Target_Lang", "Dubbing_Lang"]:
                v = lang_human_readable(v)
            lines.append(f"{label}: {v}")

        # 8.2) VIDEO
        lines.append("\n" + getattr(messages, "INFO_Video"))
        for k, v in self.data["video_file"].items():
            label = getattr(messages, f"INFO_Video_{k}", k)
            if isinstance(v, float):
                lines.append(f"{label}: {v:.2f}")
            else:
                lines.append(f"{label}: {v}")

        # 8.3) AUDIO TRACKS
        lines.append("\n" + getattr(messages, "INFO_Audio"))
        for idx, t in enumerate(self.data["audio_tracce"], start=1):
            lines.append(f"{getattr(messages, 'INFO_Audio_Traccia').format(idx)}:")
            for k, v in t.items():
                label = getattr(messages, f"INFO_Audio_{k}", k)
                if isinstance(v, float):
                    lines.append(f"  {label}: {v:.2f}")
                else:
                    lines.append(f"  {label}: {v}")

        # 8.4) TRANSCRIPTION (versione leggibile)
        lines.append("\n" + getattr(messages, "INFO_Transcript"))
        for k, v in self.data["trascrizione"].items():
            label = getattr(messages, f"INFO_Transcript_{k}", k)
            if k == "files" and isinstance(v, dict):
                lines.append(f"{label}:")
                for tipo, dati in v.items():
                    lines.append(f"  {tipo.capitalize()}:")
                    for fk, fv in dati.items():
                        lines.append(f"    {fk}: {fv}")
            else:
                lines.append(f"{label}: {v}")

        # 8.5) TRANSLATIONS
        lines.append("\n" + getattr(messages, "INFO_Translate"))
        for k, v in self.data["traduzioni"].items():
            label = getattr(messages, f"INFO_Translate_{k}", k)
            # se i campi sono codici lingua, renderizzarli umanamente
            if k in ["source_lang", "target_lang"]:
                v = getattr(messages, f'LANG_{v}', v)
            lines.append(f"{label}: {v}")

        # 8.6) TTS
        lines.append("\n" + getattr(messages, "INFO_TTS"))
        for motore, v in self.data["TTS"].items():
            label_motore = getattr(messages, f"INFO_TTS_{motore}", motore)
            lines.append(f"{label_motore}:")
            for k, val in v.items():
                label = getattr(messages, f"INFO_TTS_{k}", k)
                lines.append(f"  {label}: {val}")

        # 8.7) Write info file
        with open(self.info_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    # =========================================================
    # 9) Analyze video file with ffprobe
    # =========================================================
    def analyze_video(self, video_path, ffprobe_path=None):
        video_path = str(Path(video_path).resolve())
        dimensione_MB = os.path.getsize(video_path) / (1024 * 1024) if os.path.exists(video_path) else 0
        if not Path(video_path).exists():
            logging.warning(f"Video not found: {video_path}")
            return

        durata_s = None
        codec_video = None
        frame_rate = None
        risoluzione = None

        if ffprobe_path and Path(ffprobe_path).exists():
            try:
                # 9.1) Duration
                cmd_duration = [ffprobe_path, '-v', 'error', '-show_entries',
                                'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
                result = subprocess.run(cmd_duration, capture_output=True, text=True)
                durata_s = float(result.stdout.strip()) if result.stdout.strip() else None

                # 9.2) Codec, frame rate, resolution
                cmd_stream = [ffprobe_path, '-v', 'error', '-select_streams', 'v:0',
                              '-show_entries', 'stream=codec_name,width,height,r_frame_rate',
                              '-of', 'default=noprint_wrappers=1', video_path]
                result = subprocess.run(cmd_stream, capture_output=True, text=True)
                for line in result.stdout.strip().splitlines():
                    if line.startswith("codec_name="):
                        codec_video = line.split('=')[1]
                    elif line.startswith("width="):
                        width = int(line.split('=')[1])
                    elif line.startswith("height="):
                        height = int(line.split('=')[1])
                        risoluzione = f"{width}x{height}"
                    elif line.startswith("r_frame_rate="):
                        fr = line.split('=')[1]
                        if '/' in fr:
                            num, denom = fr.split('/')
                            frame_rate = round(float(num)/float(denom), 2) if float(denom) != 0 else None

            except Exception as e:
                logging.warning(f"Error analyzing video {video_path}: {e}")

        # 9.3) Save video data
        self.update_video_file(
            path=video_path,
            durata_s=durata_s,
            codec_video=codec_video,
            frame_rate=frame_rate,
            risoluzione=risoluzione
        )

    # =========================================================
    # 10) Update audio track count in video_file
    # =========================================================
    def set_audio_track_count(self, count):
        """
        Update the number of audio tracks in video_file without altering other info.
        """
        if "video_file" not in self.data:
            self.data["video_file"] = {}
        self.data["video_file"]["audio_tracce"] = count
        self.save_json()
        
    # =========================================================
    # 11) Merge/update arbitrary section in JSON
    # =========================================================
    def update_section_with_merge(self, section_name, new_data, merge=True):
        """
        Aggiorna o crea una sezione del JSON, facendo merge con i dati esistenti se richiesto.
        
        section_name : str
            Nome della sezione da aggiornare, es. "trascrizione", "traduzioni", "TTS"
        new_data : dict
            Dati da inserire/aggiornare nella sezione
        merge : bool
            Se True, unisce con i dati esistenti; se False, sovrascrive completamente
        """
        if section_name not in self.data or not isinstance(self.data[section_name], dict):
            self.data[section_name] = {}

        if merge:
            # Merge dati nuovi con quelli esistenti
            self.data[section_name].update(new_data)
        else:
            # Sovrascrivi completamente
            self.data[section_name] = new_data

        # Aggiorna timestamp di ultima modifica
        self.data["progetto"]["ultima_modifica"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_json()
        
    # =========================================================
    # Funzione globale per analizzare file SRT (versione migliorata)
    # =========================================================
    def analizza_file_srt(self, file_path, file_not_present_label):
        if file_path and os.path.exists(file_path):
            blocchi = 0
            tot_caratteri = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                blocco_corrente = []
                for line in f:
                    line = line.strip()
                    if line == "":
                        if blocco_corrente:
                            blocchi += 1
                            # Salta numero e timestamp, somma solo testo
                            tot_caratteri += sum(len(l) for l in blocco_corrente[2:])
                            blocco_corrente = []
                    else:
                        blocco_corrente.append(line)
                # Conta l’ultimo blocco se il file non termina con linea vuota
                if blocco_corrente:
                    blocchi += 1
                    tot_caratteri += sum(len(l) for l in blocco_corrente[2:])
            return {
                "file_srt": str(Path(file_path).resolve()),
                "numero_blocchi": blocchi,
                "tot_caratteri": tot_caratteri
            }
        else:
            return {
                "file_srt": file_not_present_label,
                "numero_blocchi": 0,
                "tot_caratteri": 0
            }

    def _inherit_previous(self):
        """
        Importa i dati dal JSON precedente senza sovrascrivere
        la sezione che verrà aggiornata nello script corrente.
        """

        if not os.path.exists(self.source_json):
            return

        try:
            with open(self.source_json, "r", encoding="utf-8") as f:
                source_data = json.load(f)

            for section, value in source_data.items():

                # non sovrascrivere la sezione corrente
                if section == self.current_section:
                    continue

                if section not in self.data:
                    self.data[section] = value
                    continue

                if isinstance(value, dict):

                    if not self.data[section]:
                        self.data[section] = value
                    else:
                        for k, v in value.items():
                            if k not in self.data[section]:
                                self.data[section][k] = v

                elif isinstance(value, list):

                    if not self.data[section]:
                        self.data[section] = value

            self.save_json()

        except Exception as e:
            logging.warning(f"Error inheriting JSON from {self.source_json}: {e}")
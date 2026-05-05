# =========================================================
# [1] Header
# =========================================================
"""
Voices Repository - Dubbing Toolkit
-----------------------------------
Script standalone per generare repository audio delle voci TTS
Azure e Google, usando le voci filtrate e le frasi di test.
"""

# =========================================================
# [2] Import
# =========================================================
import sys
import json
from pathlib import Path
from google.cloud import texttospeech
import azure.cognitiveservices.speech as speechsdk
from datetime import datetime

# Aggiunge la cartella principale al path per importare core e altri moduli
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from core.credentials_manager import get_provider_credentials
from Scripts.monitoraggio_consumo import ConsumoTTS

# =========================================================
# [4] Percorsi
# =========================================================
VOICES_OUTPUT_DIR = ROOT_DIR / "voices" / "voices_output"
AZURE_VOICES_FILE = ROOT_DIR / "voices" / "voices_azure.json"
GOOGLE_VOICES_FILE = ROOT_DIR / "voices" / "voices_google.json"
TEST_SENTENCES_FILE = ROOT_DIR / "voices" / "voices_test_sentences.json"
LOG_FILE = VOICES_OUTPUT_DIR / "synthesis_log.txt"
VOICES_INDEX_FILE = ROOT_DIR / "voices" / "voices_index.json"

# =========================================================
# [4d] Filtro lingue (opzionale)
# =========================================================
# Inserisci qui le lingue che vuoi generare.
# Esempio: {"en", "it"} -> solo inglese e italiano
# Per generare tutte le lingue, basta mettere set() vuoto.
def extract_base_language(lang_code):
    return lang_code.split("-")[0].lower()
    
#DESIRED_LANGUAGES = {"en", "it"}  # genera solo inglese e italiano
DESIRED_LANGUAGES = set()       # genera tutte le lingue senza filtro

# =========================================================
# [4b] Header log (solo se non esiste)
# =========================================================
if not LOG_FILE.exists():
    VOICES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("TIMESTAMP           | PROVID | VOICE_TAG                           | STAT  | FILE\n")

# 4c variabili
MIN_FILE_SIZE_BYTES = 5000  # 5 KB per sicurezza, sufficiente a filtrare file vuoti o parziali


# =========================================================
# [5] Utility JSON
# =========================================================
# Carica un file JSON e restituisce i dati come oggetto Python

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Scansiona le voci dai JSON dei provider e costruisce l'indice completo unificato
def build_voices_index():
    voices = []

    provider_json_files = [
        ("azure", AZURE_VOICES_FILE),
        ("google", GOOGLE_VOICES_FILE)
    ]

    for provider_name, provider_file in provider_json_files:
        data = load_json(provider_file)

        for voice in data.get("voices", []):
            audio_file = VOICES_OUTPUT_DIR / provider_name / voice["languageCodes"].upper() / f"{voice.get('api_tag', voice['name'])}.mp3"

            # Usa solo file validi
            if not audio_file.exists() or audio_file.stat().st_size < MIN_FILE_SIZE_BYTES:
                continue

            rel_path = audio_file.relative_to(ROOT_DIR)

            voices.append({
                "provider": provider_name,
                "api_tag": voice.get("api_tag", voice["name"]),
                "display_name": voice.get("display_name", voice.get("name")),
                "gender": voice.get("ssmlGender", "Unknown").capitalize(),
                "engine": voice.get("engine", "Unknown"),
                "language": voice.get("languageCodes", "").split("-")[0],
                "language_code": voice.get("languageCodes", ""),
                "path": str(rel_path)
            })

    return voices


def save_voices_index(voices):
    with open(VOICES_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(voices, f, indent=2, ensure_ascii=False)
# =========================================================
# [6] Credenziali e client TTS
# =========================================================
def init_azure_speech():
    key, region = get_provider_credentials("azure").values()
    config = speechsdk.SpeechConfig(subscription=key, region=region)
    config.speech_synthesis_output_format = speechsdk.SpeechSynthesisOutputFormat.Audio16Khz128KBitRateMonoMp3
    return config

def init_google_client():
    creds = get_provider_credentials("google")
    client = texttospeech.TextToSpeechClient.from_service_account_info(creds)
    return client

# =========================================================
# [7] Log
# =========================================================
def log_message(provider, voice_tag, file_path, status):
    VOICES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"{timestamp} | "
        f"{provider:<6} | "
        f"{voice_tag:<35} | "
        f"{status:<5} | "
        f"{file_path}"
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# =========================================================
# [8] Creazione cartelle output
# =========================================================
def ensure_output_dir(provider, voice_entry):
    provider = provider.lower()  # cartella provider in minuscolo
    lang_code = voice_entry["languageCodes"].upper()  # lingua e regione maiuscole
    dir_path = VOICES_OUTPUT_DIR / provider / lang_code
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

# =========================================================
# [9] Sintesi vocale
# =========================================================
def synthesize_azure_text(speech_config, voice_name, text, output_file: Path, warning_list):
    try:
        consumo_azure = ConsumoTTS(motore="azure")
        consumo_azure.aggiungi_caratteri(len(text))

        output_file = output_file.with_suffix(".mp3")
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_file))
        speech_config.speech_synthesis_voice_name = voice_name
        # Controllo di sicurezza (debug definitivo)
        if not speech_config.speech_synthesis_voice_name:
            raise RuntimeError("Voce Azure non impostata!")
        
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        result = synthesizer.speak_text_async(text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            log_message("Azure", voice_name, output_file, "OK")
            print(f"Audio generato: {output_file}")

            if output_file.stat().st_size < MIN_FILE_SIZE_BYTES:
                warning_msg = f"WARNING: File Azure {voice_name} generato ma dimensione troppo piccola: {output_file.stat().st_size} bytes"
                print(warning_msg)
                log_message("Azure", voice_name, output_file, "WARNING_DIM")
                warning_list.append(voice_name)  # <- aggiunta alla lista warning
        else:
            details = getattr(result, "cancellation_details", None)
            error = getattr(details, "error_details", "Unknown")
            log_message("Azure", voice_name, output_file, f"ERROR {error}")
            print(f"Errore sintesi: {error}")

        print("Consumo Azure:", consumo_azure.report_sintesi())

    except Exception as e:
        log_message("Azure", voice_name, output_file, f"ERROR {str(e)}")
        print(f"Eccezione synth Azure: {e}")


def synthesize_google_text(client, voice_name, language_code, text, output_file: Path, warning_list):
    try:
        consumo_google = ConsumoTTS(motore="google")
        consumo_google.aggiungi_caratteri(len(text))

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_params = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(input=synthesis_input, voice=voice_params, audio_config=audio_config)

        output_file = output_file.with_suffix(".mp3")
        with open(output_file, "wb") as out:
            out.write(response.audio_content)

        if output_file.stat().st_size < MIN_FILE_SIZE_BYTES:
            warning_msg = f"WARNING: File Google {voice_name} generato ma dimensione troppo piccola: {output_file.stat().st_size} bytes"
            print(warning_msg)
            log_message("Google", voice_name, output_file, "WARNING_DIM")
            warning_list.append(voice_name)  # <- aggiunta alla lista warning

        log_message("Google", voice_name, output_file, "OK")
        print(f"Audio generato: {output_file}")
        print("Consumo Google:", consumo_google.report_sintesi())

    except Exception as e:
        log_message("Google", voice_name, output_file, f"ERROR {str(e)}")
        print(f"Eccezione synth Google: {e}")

# =========================================================
# [10] Generazione audio
# =========================================================
def generate_all_audio():
    azure_config = init_azure_speech()
    google_client = init_google_client()

    azure_voices = load_json(AZURE_VOICES_FILE)["voices"]
    google_voices = load_json(GOOGLE_VOICES_FILE)["voices"]
    test_sentences = load_json(TEST_SENTENCES_FILE)["sentences"]

    MAX_TEST_ITERATIONS = 0 # esempio: massimo per provider (0 nessun limite)
    total_generated_azure = 0
    total_generated_google = 0
    total_skipped_azure = 0
    total_skipped_google = 0
    processed_azure = 0
    processed_google = 0
    # Liste per warning
    azure_warnings = []
    google_warnings = []

    # ------------------------
    # Azure
    # ------------------------
    for voice in azure_voices:
        if MAX_TEST_ITERATIONS and total_generated_azure >= MAX_TEST_ITERATIONS:
            break

        lang_code = voice.get("languageCodes")
        if not lang_code or lang_code not in test_sentences:
            continue
            
        # -------------------------
        # FILTRO LINGUE DESIDERATE
        # -------------------------
        base_lang = extract_base_language(lang_code)

        if DESIRED_LANGUAGES and base_lang not in DESIRED_LANGUAGES:
            continue  # salta questa voce se la lingua non è nella lista

        sentence = test_sentences[lang_code]
        out_dir = ensure_output_dir("Azure", voice)
        voice_tag = voice.get("api_tag", voice["name"])
        out_file = out_dir / f"{voice_tag}.mp3"

        if out_file.exists():
            total_skipped_azure += 1
            processed_azure += 1
            continue

        try:
            print()
            print(f"[{processed_azure + 1}/{len(azure_voices)}] Azure -> {voice_tag}")
            synthesize_azure_text(azure_config, voice_tag, sentence, out_file, azure_warnings)
            total_generated_azure += 1
        except Exception as e:
            log_message("Azure", voice_tag, out_file, f"ERROR {str(e)}")

        processed_azure += 1

    # ------------------------
    # Google
    # ------------------------
    for voice in google_voices:
        if MAX_TEST_ITERATIONS and total_generated_google >= MAX_TEST_ITERATIONS:
            break

        lang_code = voice.get("languageCodes")
        if not lang_code or lang_code not in test_sentences:
            continue

        # -------------------------
        # FILTRO LINGUE DESIDERATE
        # -------------------------
        base_lang = extract_base_language(lang_code)

        if DESIRED_LANGUAGES and base_lang not in DESIRED_LANGUAGES:
            continue  # salta questa voce se la lingua non è nella lista
            
        sentence = test_sentences[lang_code]
        out_dir = ensure_output_dir("Google", voice)
        voice_tag = voice.get("api_tag", voice["name"])
        out_file = out_dir / f"{voice_tag}.mp3"

        if out_file.exists():
            total_skipped_google += 1
            processed_google += 1
            continue

        try:
            print()
            print(f"[{processed_google + 1}/{len(google_voices)}] Google -> {voice_tag}")
            synthesize_google_text(google_client, voice_tag, lang_code, sentence, out_file, google_warnings)
            total_generated_google += 1
        except Exception as e:
            log_message("Google", voice_tag, out_file, f"ERROR {str(e)}")

        processed_google += 1

    # ------------------------
    # Riepilogo
    # ------------------------
    print()
    print(f"Azure: File generati={total_generated_azure}, già presenti={total_skipped_azure}")
    print(f"Google: File generati={total_generated_google}, già presenti={total_skipped_google}")
    print("\nRepository stato:\n")
    azure_repo = total_generated_azure + total_skipped_azure
    google_repo = total_generated_google + total_skipped_google
    azure_total = len(azure_voices)
    google_total = len(google_voices)
    azure_pct = (azure_repo / azure_total) * 100
    google_pct = (google_repo / google_total) * 100
    print(f"Azure  | generati: {total_generated_azure} | repository: {azure_repo} / {azure_total} ({azure_pct:.1f}%)")
    print(f"Google | generati: {total_generated_google} | repository: {google_repo} / {google_total} ({google_pct:.1f}%)")
    
    # Riepilogo warning
    if azure_warnings or google_warnings:
        print("\nWARNINGS FILE DIMENSIONE PICCOLA:")
        if azure_warnings:
            print("Azure:", ", ".join(azure_warnings))
        if google_warnings:
            print("Google:", ", ".join(google_warnings))

        # Scrivi anche nel log
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n=== WARNING FILE DIMENSIONE PICCOLA ===\n")
            if azure_warnings:
                f.write("Azure: " + ", ".join(azure_warnings) + "\n")
            if google_warnings:
                f.write("Google: " + ", ".join(google_warnings) + "\n")
    
    else:
        print("\nNESSUN WARNING DI DIMENSIONE PICCOLA RILEVATO")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n=== NESSUN WARNING DI DIMENSIONE PICCOLA ===\n")
            
    # ------------------------
    # Costruzione indice voci
    # ------------------------
    print("\nCostruzione indice voci...")

    voices_index = build_voices_index()
    save_voices_index(voices_index)

    print(f"Indice voci salvato in: {VOICES_INDEX_FILE}")
    print(f"Totale voci indicizzate: {len(voices_index)}")
    
# =========================================================
# [11] Main
# =========================================================
if __name__ == "__main__":
    print("Generazione audio in corso...")
    generate_all_audio()
    print("Operazione completata.")
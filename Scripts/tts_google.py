# =========================================================
# tts_google.py versione aggiornata
# =========================================================
# Modulo standalone per sintesi vocale con Google TTS
# Input obbligatori: file_input, voice_name, output_dir, output_format, language_code
# Credenziali Google gestite dal progetto tramite JSON
# Parsing SRT eseguito internamente
# =========================================================

# =================== BLOCCO 1: import e PATH ===================
import sys
import os
import time
import traceback as _tb_module

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# =================== BLOCCO 2: import core ===================
from google.cloud import texttospeech
from core.credentials_manager import get_provider_credentials
from core.messages import Messages
from core.utils_tts import parse_srt
from core.logger import logger

# =================== BLOCCO 3: credenziali e messaggi ===================
google_creds = get_provider_credentials("google")
messages = Messages()

# =================== BLOCCO 4: creazione client ===================
def crea_client_google(google_creds):
    return texttospeech.TextToSpeechClient.from_service_account_info(google_creds)

client_google = crea_client_google(google_creds)

# =================== BLOCCO 5: funzione batch ===================
def sintetizza_google_batch(
    file_input,
    output_dir,
    voice_name,
    output_format,
    language_code
):
    """
    Sintetizza un file SRT.
    Parametri:
        file_input: percorso file SRT
        output_dir: cartella di output
        voice_name: nome della voce Google
        output_format: "wav" o "mp3"
        language_code: codice lingua obbligatorio (es. 'en-US')
    """

    # =================== BLOCCO 5.1: validazioni ===================
    if not os.path.isfile(file_input):
        raise FileNotFoundError(messages.TTS_Google_file_not_found.format(file_input))

    output_format = output_format.lower()
    if language_code is None:
        raise ValueError(messages.TTS_Google_language_code_missing)

    os.makedirs(output_dir, exist_ok=True)

    # =================== BLOCCO 5.2: parsing SRT ===================
    entries = parse_srt(file_input)
    if not entries:
        raise ValueError(messages.TTS_Google_no_entries)

    # =================== BLOCCO 5.3: ciclo di sintesi ===================
    for entry in entries:
        filename, testo, start_time, end_time = entry

        # Formattazione nome file: sostituisco : e , con -
        start_str = start_time.replace(":", "-").replace(",", "-")
        end_str = end_time.replace(":", "-").replace(",", "-")
        file_output = os.path.join(output_dir, f"{start_str}_{end_str}.{output_format}")

        _op_t0 = time.monotonic()
        _api_t0 = _op_t0  # fallback se l'eccezione arriva prima della chiamata API
        try:
            _api_t0 = time.monotonic()
            response = client_google.synthesize_speech(
                input=texttospeech.SynthesisInput(text=testo),
                voice=texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name),
                audio_config=texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3
                    if output_format == "mp3"
                    else texttospeech.AudioEncoding.LINEAR16
                )
            )
            _api_ms = round((time.monotonic() - _api_t0) * 1000)

            with open(file_output, "wb") as out:
                out.write(response.audio_content)

            _dur_ms = round((time.monotonic() - _op_t0) * 1000)
            logger.operation("tts_google", "sintetizza_google_batch",
                             "Google TTS synthesis completed",
                             status="SUCCESS", duration_ms=_dur_ms, api_latency_ms=_api_ms,
                             context={"voice": voice_name, "text_length": len(testo),
                                      "file": os.path.basename(file_output),
                                      "language_code": language_code})

        except Exception as e:
            _api_ms = round((time.monotonic() - _api_t0) * 1000)
            _dur_ms = round((time.monotonic() - _op_t0) * 1000)
            print(messages.TTS_Google_synthesis_error.format(file_output, e))
            logger.error("tts_google", "sintetizza_google_batch", str(e),
                         error_code="TTS_GOOGLE_EXCEPTION", error_category="API",
                         is_retryable=True,
                         context={"voice": voice_name, "text_length": len(testo),
                                  "language_code": language_code,
                                  "api_latency_ms": _api_ms, "duration_ms": _dur_ms},
                         traceback=_tb_module.format_exc())

# =================== BLOCCO 6: main CLI ===================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=messages.TTS_Google_cli_description)
    parser.add_argument("--voice", required=True, help=messages.TTS_Google_cli_voice)
    parser.add_argument("--input", required=True, help=messages.TTS_Google_cli_input)
    parser.add_argument("--output_dir", required=True, help=messages.TTS_Google_cli_output_dir)
    parser.add_argument("--format", required=True, choices=["wav", "mp3"], help=messages.TTS_Google_cli_format)
    parser.add_argument("--language", required=True, help="Codice lingua obbligatorio, es. 'en-US'")

    args = parser.parse_args()

    # =================== BLOCCO 6.1: chiamata batch ===================
    sintetizza_google_batch(
        file_input=args.input,
        output_dir=args.output_dir,
        voice_name=args.voice,
        output_format=args.format.lower(),
        language_code=args.language
    )
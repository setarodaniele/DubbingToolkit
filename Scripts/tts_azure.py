# =========================================================
# tts_azure.py versione aggiornata
# =========================================================
# Modulo standalone per sintesi vocale con Azure TTS
# Input obbligatori: file_input, voice_name, output_dir, output_format
# Credenziali Azure gestite dal progetto tramite JSON
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
import azure.cognitiveservices.speech as speechsdk
from core.credentials_manager import get_provider_credentials
from core.messages import Messages
from core.utils_tts import parse_srt  # parser condiviso
from core.logger import logger

# =================== BLOCCO 3: credenziali e messaggi ===================
azure_creds = get_provider_credentials("azure")
azure_key = azure_creds["subscription"]
azure_region = azure_creds["region"]
messages = Messages()

# =================== BLOCCO 4: creazione SpeechConfig ===================
def crea_speech_config(azure_key, azure_region, voice_name, output_format="wav"):
    speech_config = speechsdk.SpeechConfig(subscription=azure_key, region=azure_region)
    speech_config.speech_synthesis_voice_name = voice_name

    if output_format.lower() == "wav":
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
        )
    elif output_format.lower() == "mp3":
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3
        )
    else:
        raise ValueError(messages.TTS_Azure_unsupported_format.format(output_format))

    return speech_config

# =================== BLOCCO 5: funzione batch ===================
def sintetizza_azure_batch(
    file_input,
    output_dir,
    voice_name,
    output_format
):
    """
    Sintetizza un file SRT con Azure TTS.
    Parametri:
        file_input: percorso file SRT
        output_dir: cartella di output
        voice_name: nome della voce Azure
        output_format: "wav" o "mp3"
    """

    if not os.path.isfile(file_input):
        raise FileNotFoundError(messages.TTS_Azure_file_not_found.format(file_input))

    output_format = output_format.lower()
    os.makedirs(output_dir, exist_ok=True)

    # =================== BLOCCO 5.1: creazione SpeechConfig ===================
    speech_config = crea_speech_config(
        azure_key,
        azure_region,
        voice_name,
        output_format
    )

    # =================== BLOCCO 5.2: parsing SRT ===================
    entries = parse_srt(file_input)
    if not entries:
        raise ValueError(messages.TTS_Azure_no_entries)

    # =================== BLOCCO 5.3: ciclo di sintesi ===================
    file_ext = "mp3" if output_format == "mp3" else "wav"

    _MAX_RETRIES = 3
    _RETRY_DELAYS = [2, 5, 10]  # secondi di attesa tra i tentativi

    for entry in entries:
        _, testo, start_time, end_time = entry

        start_str = start_time.replace(":", "-").replace(",", "-")
        end_str = end_time.replace(":", "-").replace(",", "-")
        file_output = os.path.join(output_dir, f"{start_str}_{end_str}.{file_ext}")

        success = False
        for attempt in range(1, _MAX_RETRIES + 1):
            _op_t0 = time.monotonic()
            _api_t0 = _op_t0
            try:
                audio_config = speechsdk.audio.AudioOutputConfig(filename=file_output)
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=speech_config,
                    audio_config=audio_config
                )

                _api_t0 = time.monotonic()
                result = synthesizer.speak_text_async(testo).get()
                _api_ms = round((time.monotonic() - _api_t0) * 1000)
                _dur_ms = round((time.monotonic() - _op_t0) * 1000)

                if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
                    cancellation_details = getattr(result, "cancellation_details", None)
                    error_details = getattr(cancellation_details, "error_details", "") if cancellation_details else ""
                    error_code_azure = str(getattr(cancellation_details, "error_code", "")) if cancellation_details else ""
                    # Rimuove il file corrotto/vuoto lasciato da Azure SDK
                    if os.path.exists(file_output):
                        try:
                            os.remove(file_output)
                        except OSError:
                            pass
                    if attempt < _MAX_RETRIES:
                        delay = _RETRY_DELAYS[attempt - 1]
                        print(messages.TTS_Azure_synthesis_error.format(result.reason, error_details)
                              + f" — retry {attempt}/{_MAX_RETRIES - 1} in {delay}s...")
                        time.sleep(delay)
                        continue
                    # Tutti i tentativi esauriti
                    print(messages.TTS_Azure_synthesis_error.format(result.reason, error_details))
                    logger.error("tts_azure", "sintetizza_azure_batch",
                                 f"Azure synthesis failed after {attempt} attempts: {result.reason}",
                                 error_code="TTS_AZURE_SYNTHESIS_FAILED", error_category="API",
                                 is_retryable=False,
                                 context={"voice": voice_name, "text_length": len(testo),
                                          "reason": str(result.reason),
                                          "azure_error_code": error_code_azure,
                                          "azure_error_details": error_details,
                                          "attempts": attempt,
                                          "api_latency_ms": _api_ms, "duration_ms": _dur_ms})
                else:
                    logger.operation("tts_azure", "sintetizza_azure_batch",
                                     "Azure TTS synthesis completed",
                                     status="SUCCESS", duration_ms=_dur_ms, api_latency_ms=_api_ms,
                                     context={"voice": voice_name, "text_length": len(testo),
                                              "file": os.path.basename(file_output),
                                              "attempt": attempt})
                    success = True

            except Exception as e:
                _api_ms = round((time.monotonic() - _api_t0) * 1000)
                _dur_ms = round((time.monotonic() - _op_t0) * 1000)
                # Rimuove il file corrotto/vuoto per evitare crash in tts_merge.py
                if os.path.exists(file_output):
                    try:
                        os.remove(file_output)
                    except OSError:
                        pass
                if attempt < _MAX_RETRIES:
                    delay = _RETRY_DELAYS[attempt - 1]
                    print(messages.TTS_Azure_synthesis_error.format("Exception", e)
                          + f" — retry {attempt}/{_MAX_RETRIES - 1} in {delay}s...")
                    time.sleep(delay)
                    continue
                print(messages.TTS_Azure_synthesis_error.format("Exception", e))
                logger.error("tts_azure", "sintetizza_azure_batch", str(e),
                             error_code="TTS_AZURE_EXCEPTION", error_category="API",
                             is_retryable=False,
                             context={"voice": voice_name, "text_length": len(testo),
                                      "attempts": attempt,
                                      "api_latency_ms": _api_ms, "duration_ms": _dur_ms},
                             traceback=_tb_module.format_exc())

            break  # esce dal loop retry (successo o errore finale loggato)

        _ = success  # usato per debug futuro se necessario

# =================== BLOCCO 6: main CLI ===================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=messages.TTS_Azure_cli_description)
    parser.add_argument("--voice", required=True, help=messages.TTS_Azure_cli_voice)
    parser.add_argument("--input", required=True, help=messages.TTS_Azure_cli_input)
    parser.add_argument("--output_dir", required=True, help=messages.TTS_Azure_cli_output_dir)
    parser.add_argument("--format", required=True, choices=["wav", "mp3"], help=messages.TTS_Azure_cli_format)

    args = parser.parse_args()

    # Chiamata batch
    sintetizza_azure_batch(
        file_input=args.input,
        output_dir=args.output_dir,
        voice_name=args.voice,
        output_format=args.format.lower()
    )
# Limitations and Notes

This document transparently collects the current limitations of DubbingToolkit, features not yet implemented, and known behaviors that may not match expectations. The project is under active development and these limitations are intended to be resolved progressively.

---

## Non-Persistent Settings

Settings are not saved between sessions. On every startup the system resets to default values and asks for the interface language. All other preferences — TTS provider, voice, Whisper model, transcription and translation languages — must be reselected each time. Settings persistence is planned as a future improvement.

---

## No Batch Mode

The workflow is designed to process one file at a time. There is no mode for automatically processing multiple files in sequence. This feature is being considered for future development.

---

## Translation Quality

Translation uses Helsinki-NLP models running locally. Quality may be lower than professional cloud translation services, especially on idiomatic phrases, technical terms, or text with irregular punctuation. Manual review of translated text before proceeding to synthesis is always recommended.

---

## No Automatic Timing Verification

After translation, the text may be longer or shorter than the original, creating mismatches with the speech timing in the video. There is currently no automatic verification or adaptation system. Timing management requires manual intervention on the translated SRT file. An automatic verification and adaptation system is planned as a future improvement.

---

## Transcription: Automatic Language Detection

Whisper automatically detects the spoken language, but can make errors on noisy audio, strong accents, or low-quality recordings. In these cases, it is necessary to manually specify the language before transcription. A detection confidence evaluation system is planned as a future improvement.

---

## Transcription: Memory Management

Very long audio files are loaded entirely into memory during transcription. On systems with limited RAM this can cause slowdowns or interruptions. Chunk-based processing is planned as a future improvement.

---

## WhisperX Not Integrated

The WhisperX environment is prepared but not yet integrated into the main pipeline. Standard Whisper is exclusively used at this time.

---

## Subtitles Not Available

The subtitle export function is present in the menu but not yet implemented. Selecting it produces no output.

---

## Additional TTS Providers Not Connected

Azure and Google are currently supported. Integration of additional providers, including OpenAI and ElevenLabs, is planned for the future.

---

## Pivot Translation Not Available

If the direct source-to-target language pair is not available in the Helsinki-NLP models, translation is not possible. Translation via pivot language (English as intermediate) is planned but not yet implemented.

---

## Limited Portability

The project can be moved to a different location but requires rebuilding the virtual environment after every move. It is not a fully portable system.

---

## Sequential Processing

Pipeline stages are executed sequentially. It is not possible to parallelize the processing of multiple files or run stages concurrently.

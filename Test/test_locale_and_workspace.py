# =========================================================
# Test/test_locale_and_workspace.py
# =========================================================
# Automated tests covering:
#   1. JSON validity — all 8 locale files
#   2. is_yes() — all 8 locales, YES + NO + edge cases
#   3. offer_open_folder — logic without opening Explorer
#   4. WorkspaceManager — create / duplicate / rename / delete (use_trash + shutil)
#   5. source_importer._find_projects_referencing
# =========================================================

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import importlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"

_results: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    _results.append((name, condition, detail))
    print(f"  [{status}] {name}" + (f"  ({detail})" if detail and not condition else ""))


# =========================================================
# 1. JSON validity — all 8 locale files
# =========================================================

def test_locale_json_validity():
    print("\n-- 1. JSON validity (all locales) --")
    locale_dir = ROOT / "locale" / "Active"
    expected_langs = {"de", "en", "es", "fr", "it", "pt", "ru", "zh"}
    found = {p.stem for p in locale_dir.glob("*.json")}
    check("All 8 locale files present", expected_langs <= found,
          f"missing: {expected_langs - found}" if not expected_langs <= found else "")

    for lang in sorted(expected_langs & found):
        path = locale_dir / f"{lang}.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            ok = isinstance(data, dict)
        except Exception as e:
            ok = False
            check(f"{lang}.json parses OK", ok, str(e))
            continue
        check(f"{lang}.json parses OK", ok)

        for key in ("YES_SHORT", "YES_FULL", "GENERAL_YES"):
            check(f"{lang} has key '{key}'", key in data and bool(data[key]))


# =========================================================
# 2. is_yes() — all 8 locales
# =========================================================

def _make_messages(lang_data: dict) -> SimpleNamespace:
    ns = SimpleNamespace()
    for k, v in lang_data.items():
        setattr(ns, k, v)
    return ns


def test_is_yes_all_locales():
    print("\n--2. is_yes() — all 8 locales --")
    from core.input_parsing import is_yes

    locale_dir = ROOT / "locale" / "Active"
    yes_map = {
        "it": ["s", "S", "si", "Si", "Sì", "sì"],
        "en": ["y", "Y", "yes", "Yes", "YES"],
        "de": ["j", "J", "ja", "Ja", "JA"],
        "es": ["s", "S", "sí", "Sí", "SÍ"],
        "fr": ["o", "O", "oui", "Oui", "OUI"],
        "pt": ["s", "S", "sim", "Sim", "SIM"],
        "ru": ["д", "Д", "да", "Да", "ДА"],
        "zh": ["是"],
    }
    no_map = {
        "it": ["n", "no", "NO", "x", ""],
        "en": ["n", "no", "NO", "x", ""],
        "de": ["n", "nein", "x", ""],
        "es": ["n", "no", "x", ""],
        "fr": ["n", "non", "x", ""],
        "pt": ["n", "não", "x", ""],
        "ru": ["н", "нет", "x", ""],
        "zh": ["否", "n", "x", ""],
    }

    for lang in sorted(yes_map):
        path = locale_dir / f"{lang}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        msg = _make_messages(data)

        for ans in yes_map[lang]:
            check(f"{lang}: is_yes('{ans}') == True", is_yes(ans, msg))

        for ans in no_map[lang]:
            check(f"{lang}: is_yes('{ans}') == False", not is_yes(ans, msg))


# =========================================================
# 3. offer_open_folder — logic (no Explorer)
# =========================================================

def test_offer_open_folder():
    print("\n--3. offer_open_folder logic --")
    from core.ui_printer import offer_open_folder

    en_data = json.loads((ROOT / "locale" / "Active" / "en.json").read_text(encoding="utf-8"))
    it_data = json.loads((ROOT / "locale" / "Active" / "it.json").read_text(encoding="utf-8"))
    msg_en = _make_messages(en_data)
    msg_it = _make_messages(it_data)

    opened = []

    with patch("os.startfile", side_effect=lambda p: opened.append(p)):
        # EN: answer 'y' → opens folder
        with patch("builtins.input", return_value="y"):
            offer_open_folder("fake_en", msg_en)
        check("EN 'y' → opens folder", len(opened) == 1)

        opened.clear()

        # EN: answer 'n' → does NOT open
        with patch("builtins.input", return_value="n"):
            offer_open_folder("fake_en_no", msg_en)
        check("EN 'n' → no open", len(opened) == 0)

        # IT: answer 's' → opens folder
        with patch("builtins.input", return_value="s"):
            offer_open_folder("fake_it", msg_it)
        check("IT 's' → opens folder", len(opened) == 1)

        opened.clear()

        # IT: answer 'n' → does NOT open
        with patch("builtins.input", return_value="n"):
            offer_open_folder("fake_it_no", msg_it)
        check("IT 'n' → no open", len(opened) == 0)

        # Empty answer → does NOT open
        with patch("builtins.input", return_value=""):
            offer_open_folder("fake_empty", msg_en)
        check("empty answer → no open", len(opened) == 0)


# =========================================================
# 4. WorkspaceManager — isolated in a temp directory
# =========================================================

def test_workspace_manager():
    print("\n--4. WorkspaceManager --")
    import core.workspace_manager as wm
    from core.workspace_manager import WorkspaceManager, WorkspaceError

    with tempfile.TemporaryDirectory(prefix="dubtest_ws_") as td:
        tmp = Path(td)
        projects = tmp / "projects"
        projects.mkdir(parents=True, exist_ok=True)
        active_file = tmp / "active_workspace.json"

        with patch.multiple(
            "core.workspace_manager",
            _PROJECTS_DIR=projects,
            _ACTIVE_FILE=active_file,
            _WORKSPACE_DIR=tmp,
        ):
            WM = wm.WorkspaceManager
            WE = wm.WorkspaceError

            # 4a. create
            ws = WM.create_project("alpha")
            check("create_project: folder exists", (projects / "alpha").exists())
            active = WM.get_active()
            check("create_project: sets as active", active is not None and active.name == "alpha")

            # 4b. duplicate
            WM.duplicate_project("alpha", "alpha_copy")
            check("duplicate_project: copy folder exists", (projects /"alpha_copy").exists())
            # original still exists
            check("duplicate_project: original intact", (projects /"alpha").exists())

            # 4c. rename
            WM.rename_project("alpha_copy", "beta")
            check("rename_project: new name exists", (projects /"beta").exists())
            check("rename_project: old name gone", not (projects /"alpha_copy").exists())

            # 4d. rename active project → pointer updates
            # alpha is still active; rename it
            WM.rename_project("alpha", "alpha_renamed")
            new_active = WM.get_active()
            check("rename active: pointer updated", new_active is not None and new_active.name == "alpha_renamed")

            # 4e. delete with use_trash=False (shutil)
            WM.delete_project("beta", use_trash=False)
            check("delete (shutil): folder gone", not (projects /"beta").exists())

            # 4f. delete active → active cleared
            WM.delete_project("alpha_renamed", use_trash=False)
            check("delete active: pointer cleared", WM.get_active() is None)

            # 4g. create duplicate name → error
            WM.create_project("gamma")
            try:
                WM.create_project("gamma")
                check("create duplicate name → WorkspaceError", False)
            except WE:
                check("create duplicate name → WorkspaceError", True)

            # 4h. list_projects
            projects_list = WM.list_projects()
            check("list_projects contains 'gamma'", "gamma" in projects_list)

            # 4i. delete with use_trash=True (send2trash if available, else shutil fallback)
            WM.create_project("trash_target")
            check("trash target created", (projects /"trash_target").exists())
            try:
                WM.delete_project("trash_target", use_trash=True)
                check("delete use_trash=True: folder gone", not (projects /"trash_target").exists())
            except Exception as e:
                check("delete use_trash=True: no exception", False, str(e))



# =========================================================
# 5. source_importer._find_projects_referencing
# =========================================================

def test_find_projects_referencing():
    print("\n--5. source_importer._find_projects_referencing --")
    import core.source_importer as si

    with tempfile.TemporaryDirectory(prefix="dubtest_src_") as td:
        tmp = Path(td)
        projects_dir = tmp / "projects"

        # Create two fake projects
        proj_a = projects_dir / "projA"
        proj_b = projects_dir / "projB"
        proj_a.mkdir(parents=True)
        proj_b.mkdir(parents=True)

        target_file = tmp / "video.mp4"
        target_file.write_text("fake")

        # projA references the file
        (proj_a / "project_info.json").write_text(
            json.dumps({"source": str(target_file.resolve())}), encoding="utf-8"
        )
        # projB does NOT reference the file
        (proj_b / "project_info.json").write_text(
            json.dumps({"source": "/other/path/video.mp4"}), encoding="utf-8"
        )

        with patch.object(si, "_PROJECTS_DIR", projects_dir):
            refs = si._find_projects_referencing(target_file)

        check("finds projA as referencing", "projA" in refs)
        check("does NOT include projB", "projB" not in refs)
        check("only 1 reference found", len(refs) == 1)

        # File not referenced by anyone
        other_file = tmp / "other.mp4"
        other_file.write_text("fake")
        with patch.object(si, "_PROJECTS_DIR", projects_dir):
            refs2 = si._find_projects_referencing(other_file)
        check("no references for unknown file", refs2 == [])


# =========================================================
# 6. InfoManager — pipeline section updates
# =========================================================

def test_info_manager_pipeline_sections():
    print("\n--6. InfoManager pipeline sections --")
    import tempfile

    scripts_dir = str(ROOT / "Scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from info_manager import InfoManager

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        im = InfoManager(base)

        # 6.1 update_trascrizione
        im.update_trascrizione("track_01", {
            "created_at":       "2026-01-01T10:00:00",
            "whisper_model":    "small",
            "spoken_lang":      "it",
            "detected_lang":    "it",
            "lang_probability": 0.987,
            "audio_duration_s": 123.45,
            "segments_count":   42,
        })
        data = json.loads((base / "project_info.json").read_text(encoding="utf-8"))
        check("trascrizione[track_01] whisper_model", data["trascrizione"]["track_01"]["whisper_model"] == "small")
        check("trascrizione[track_01] segments_count", data["trascrizione"]["track_01"]["segments_count"] == 42)

        # 6.2 update_traduzione
        im.update_traduzione("track_01", {
            "created_at":          "2026-01-01T10:05:00",
            "translation_model":   "Helsinki-NLP/opus-mt-it-en",
            "source_lang":         "it",
            "target_lang":         "en",
            "segments_translated": 42,
        })
        data = json.loads((base / "project_info.json").read_text(encoding="utf-8"))
        check("traduzioni[track_01] source_lang", data["traduzioni"]["track_01"]["source_lang"] == "it")
        check("traduzioni[track_01] target_lang", data["traduzioni"]["track_01"]["target_lang"] == "en")

        # 6.3 update_tts
        im.update_tts("track_01", {
            "created_at":      "2026-01-01T10:10:00",
            "provider":        "google",
            "voice":           "it-IT-Wavenet-A",
            "language_code":   "it-IT",
            "output_format":   "mp3",
            "characters_used": 3500,
        })
        data = json.loads((base / "project_info.json").read_text(encoding="utf-8"))
        check("TTS[track_01] provider", data["TTS"]["track_01"]["provider"] == "google")
        check("TTS[track_01] characters_used", data["TTS"]["track_01"]["characters_used"] == 3500)

        # 6.4 second track accumulates without overwriting first
        im.update_trascrizione("track_02", {
            "created_at":       "2026-01-01T10:15:00",
            "whisper_model":    "medium",
            "spoken_lang":      "en",
            "detected_lang":    "en",
            "lang_probability": 0.995,
            "audio_duration_s": 60.0,
            "segments_count":   20,
        })
        data = json.loads((base / "project_info.json").read_text(encoding="utf-8"))
        check("track_01 still present after track_02 added", "track_01" in data["trascrizione"])
        check("track_02 added", data["trascrizione"]["track_02"]["whisper_model"] == "medium")

        # 6.5 generate_info_file renders pipeline sections in TXT
        im.data["progetto"] = {"nome_progetto": "TestProject"}
        from types import SimpleNamespace as _NS
        msg = _NS(
            INFO_Progetto="=== PROJECT ===",
            INFO_Video="=== VIDEO ===",
            INFO_Audio="=== AUDIO ===",
            INFO_Audio_Traccia="Track {}",
            INFO_Trascrizione="=== TRASCRIZIONE ===",
            INFO_Traduzioni="=== TRADUZIONI ===",
            INFO_TTSDoppiaggio="=== DOPPIAGGIO TTS ===",
            INFO_StoricRinomina="=== RENAME HISTORY ===",
            INFO_StoricRinomina_entry="{data}: {da} -> {a}",
        )
        im.generate_info_file(msg)
        txt = (base / "project_info.txt").read_text(encoding="utf-8")
        check("TXT contains trascrizione header", "=== TRASCRIZIONE ===" in txt)
        check("TXT contains traduzioni header",   "=== TRADUZIONI ===" in txt)
        check("TXT contains TTS header",          "=== DOPPIAGGIO TTS ===" in txt)
        check("TXT contains track_01",            "track_01" in txt)
        check("TXT contains track_02",            "track_02" in txt)
        check("TXT contains whisper model value", "small" in txt)
        check("TXT contains TTS provider value",  "google" in txt)


# =========================================================
# Runner
# =========================================================

def main():
    print("=" * 52)
    print("DubbingToolkit — automated tests")
    print("=" * 52)

    test_locale_json_validity()
    test_is_yes_all_locales()
    test_offer_open_folder()
    test_workspace_manager()
    test_find_projects_referencing()
    test_info_manager_pipeline_sections()

    passed = sum(1 for _, ok, _ in _results if ok)
    failed = sum(1 for _, ok, _ in _results if not ok)
    total  = len(_results)

    print(f"\n{'=' * 52}")
    print(f"Results: {passed}/{total} passed", end="")
    if failed:
        print(f"  — \033[31m{failed} FAILED\033[0m")
        for name, ok, detail in _results:
            if not ok:
                print(f"  \033[31mFAIL\033[0m {name}" + (f" ({detail})" if detail else ""))
    else:
        print(f"  — \033[32mAll OK\033[0m")
    print("=" * 52)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

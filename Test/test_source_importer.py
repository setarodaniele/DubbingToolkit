"""
Test automatici per source_importer.ask_import.
Eseguire con: venv\Scripts\python.exe Test\test_source_importer.py
"""
import sys, json, shutil, tempfile, types, unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, "D:/RecordingStudio/DubbingToolkit")

import core.source_importer as si_module

def make_messages():
    with open("D:/RecordingStudio/DubbingToolkit/locale/Active/it.json", encoding="utf-8") as f:
        return types.SimpleNamespace(**json.load(f))

IT = make_messages()


class SourceImporterTests(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.src_file = self.tmp / "source_video.mp4"
        self.src_file.write_bytes(b"fake video content" * 100)
        self.dest_dir = self.tmp / "dest"
        self.dest_dir.mkdir()
        self.projects_dir = self.tmp / "projects"
        # Monkey-patch _PROJECTS_DIR
        self._orig_proj = si_module._PROJECTS_DIR
        si_module._PROJECTS_DIR = self.projects_dir

    def tearDown(self):
        si_module._PROJECTS_DIR = self._orig_proj
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ------------------------------------------------------------------
    # Salta dialog se il file è già dentro dest_dir
    # ------------------------------------------------------------------
    def test_skip_dialog_if_already_in_dest(self):
        internal = self.dest_dir / "video.mp4"
        internal.write_bytes(b"x")
        result_path, mode = si_module.ask_import(internal, self.dest_dir, IT)
        self.assertEqual(mode, "external")
        self.assertEqual(result_path.resolve(), internal.resolve())

    # ------------------------------------------------------------------
    # Opzione 0 — annulla
    # ------------------------------------------------------------------
    def test_cancel_returns_none(self):
        with patch("builtins.input", return_value="0"):
            result_path, mode = si_module.ask_import(self.src_file, self.dest_dir, IT)
        self.assertIsNone(result_path)
        self.assertIsNone(mode)

    # ------------------------------------------------------------------
    # Opzione 1 — usa external
    # ------------------------------------------------------------------
    def test_keep_external(self):
        with patch("builtins.input", return_value="1"):
            result_path, mode = si_module.ask_import(self.src_file, self.dest_dir, IT)
        self.assertEqual(mode, "external")
        self.assertEqual(result_path.resolve(), self.src_file.resolve())

    # ------------------------------------------------------------------
    # Opzione 2 — copia
    # ------------------------------------------------------------------
    def test_copy_into_project(self):
        with patch("builtins.input", return_value="2"):
            result_path, mode = si_module.ask_import(self.src_file, self.dest_dir, IT)
        self.assertEqual(mode, "copy")
        self.assertTrue(result_path.exists())
        self.assertTrue(self.src_file.exists())  # originale ancora presente

    # ------------------------------------------------------------------
    # Opzione 3 — sposta (nessun progetto che lo usa)
    # ------------------------------------------------------------------
    def test_move_into_project_no_warning(self):
        with patch("builtins.input", return_value="3"):
            result_path, mode = si_module.ask_import(self.src_file, self.dest_dir, IT)
        self.assertEqual(mode, "move")
        self.assertTrue(result_path.exists())
        self.assertFalse(self.src_file.exists())  # sorgente rimossa

    # ------------------------------------------------------------------
    # Opzione 3 — sposta con warning cross-project, utente annulla
    # ------------------------------------------------------------------
    def test_move_with_warning_cancel(self):
        # Crea un progetto fake che referenzia il file
        proj = self.projects_dir / "proj_A"
        proj.mkdir(parents=True)
        info = {"source_path": str(self.src_file.resolve())}
        (proj / "project_info.json").write_text(json.dumps(info), encoding="utf-8")

        # Sequenza input: sceglie "3" poi "n" alla conferma -> torna al loop -> "0" annulla
        with patch("builtins.input", side_effect=["3", "n", "0"]):
            result_path, mode = si_module.ask_import(self.src_file, self.dest_dir, IT)
        # Deve aver annullato senza spostare
        self.assertIsNone(result_path)
        self.assertTrue(self.src_file.exists())

    # ------------------------------------------------------------------
    # Opzione 3 — sposta con warning cross-project, utente conferma
    # ------------------------------------------------------------------
    def test_move_with_warning_confirm(self):
        proj = self.projects_dir / "proj_A"
        proj.mkdir(parents=True)
        info = {"source_path": str(self.src_file.resolve())}
        (proj / "project_info.json").write_text(json.dumps(info), encoding="utf-8")

        with patch("builtins.input", side_effect=["3", "s"]):
            result_path, mode = si_module.ask_import(self.src_file, self.dest_dir, IT)
        self.assertEqual(mode, "move")
        self.assertTrue(result_path.exists())
        self.assertFalse(self.src_file.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)

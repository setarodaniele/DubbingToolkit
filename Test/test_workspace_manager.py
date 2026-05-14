"""
Test automatici per WorkspaceManager.
Eseguire con: venv\Scripts\python.exe Test\test_workspace_manager.py
"""
import sys, json, shutil, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, "D:/RecordingStudio/DubbingToolkit")

import core.workspace_manager as wm_module
from core.workspace_manager import WorkspaceManager, WorkspaceError


class WorkspaceManagerTests(unittest.TestCase):

    def setUp(self):
        # Usa una directory temporanea isolata per ogni test
        self.tmp = Path(tempfile.mkdtemp())
        self.projects_dir = self.tmp / "projects"
        self.active_file  = self.tmp / "active_workspace.json"

        # Monkey-patch i path del modulo
        self._orig_projects = wm_module._PROJECTS_DIR
        self._orig_active   = wm_module._ACTIVE_FILE
        self._orig_temp     = wm_module._TEMP_DIR
        self._orig_ws       = wm_module._WORKSPACE_DIR

        wm_module._PROJECTS_DIR = self.projects_dir
        wm_module._ACTIVE_FILE  = self.active_file
        wm_module._TEMP_DIR     = self.tmp / "temp"
        wm_module._WORKSPACE_DIR = self.tmp

    def tearDown(self):
        wm_module._PROJECTS_DIR  = self._orig_projects
        wm_module._ACTIVE_FILE   = self._orig_active
        wm_module._TEMP_DIR      = self._orig_temp
        wm_module._WORKSPACE_DIR = self._orig_ws
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ------------------------------------------------------------------
    # Crea progetto
    # ------------------------------------------------------------------
    def test_create_project(self):
        ws = WorkspaceManager.create_project("alpha")
        self.assertTrue((self.projects_dir / "alpha").exists())
        self.assertEqual(ws.name, "alpha")

    def test_create_project_sets_active(self):
        WorkspaceManager.create_project("alpha")
        active = WorkspaceManager.get_active()
        self.assertIsNotNone(active)
        self.assertEqual(active.name, "alpha")

    def test_create_existing_raises(self):
        WorkspaceManager.create_project("alpha")
        with self.assertRaises(WorkspaceError):
            WorkspaceManager.create_project("alpha")

    # ------------------------------------------------------------------
    # Duplica progetto
    # ------------------------------------------------------------------
    def test_duplicate_project(self):
        WorkspaceManager.create_project("alpha")
        # Crea un project_info.json nella sorgente
        src_info = self.projects_dir / "alpha" / "project_info.json"
        src_info.write_text(json.dumps({"progetto": {"nome_progetto": "alpha"}}), encoding="utf-8")

        copy_ws = WorkspaceManager.duplicate_project("alpha", "alpha_copy")

        self.assertTrue((self.projects_dir / "alpha_copy").exists())
        self.assertEqual(copy_ws.name, "alpha_copy")

        # project_info.json nella copia deve avere il nuovo nome
        dest_info = self.projects_dir / "alpha_copy" / "project_info.json"
        data = json.loads(dest_info.read_text(encoding="utf-8"))
        self.assertEqual(data["progetto"]["nome_progetto"], "alpha_copy")

    def test_duplicate_does_not_set_as_active(self):
        WorkspaceManager.create_project("alpha")
        WorkspaceManager.duplicate_project("alpha", "alpha_copy")
        active = WorkspaceManager.get_active()
        self.assertEqual(active.name, "alpha")   # deve restare alpha

    # ------------------------------------------------------------------
    # Rinomina progetto
    # ------------------------------------------------------------------
    def test_rename_project(self):
        WorkspaceManager.create_project("alpha")
        ws = WorkspaceManager.rename_project("alpha", "beta")
        self.assertFalse((self.projects_dir / "alpha").exists())
        self.assertTrue((self.projects_dir / "beta").exists())
        self.assertEqual(ws.name, "beta")

    def test_rename_updates_active_pointer(self):
        WorkspaceManager.create_project("alpha")
        WorkspaceManager.rename_project("alpha", "beta")
        active = WorkspaceManager.get_active()
        self.assertIsNotNone(active)
        self.assertEqual(active.name, "beta")

    def test_rename_non_active_does_not_change_active(self):
        WorkspaceManager.create_project("alpha")
        WorkspaceManager.create_project("beta")
        # active è "beta" ora
        WorkspaceManager.rename_project("alpha", "alpha2")
        active = WorkspaceManager.get_active()
        self.assertEqual(active.name, "beta")

    # ------------------------------------------------------------------
    # Elimina progetto
    # ------------------------------------------------------------------
    def test_delete_project(self):
        WorkspaceManager.create_project("alpha")
        WorkspaceManager.delete_project("alpha")
        self.assertFalse((self.projects_dir / "alpha").exists())

    def test_delete_active_clears_pointer(self):
        WorkspaceManager.create_project("alpha")
        WorkspaceManager.delete_project("alpha")
        active = WorkspaceManager.get_active()
        self.assertIsNone(active)

    def test_delete_non_existing_raises(self):
        with self.assertRaises(WorkspaceError):
            WorkspaceManager.delete_project("ghost")

    def test_delete_with_trash(self):
        WorkspaceManager.create_project("alpha")
        with patch("send2trash.send2trash") as mock_trash:
            WorkspaceManager.delete_project("alpha", use_trash=True)
        mock_trash.assert_called_once()

    # ------------------------------------------------------------------
    # Apri cartella (solo che il path esiste — apertura Explorer non testabile)
    # ------------------------------------------------------------------
    def test_open_project_returns_manager(self):
        WorkspaceManager.create_project("alpha")
        WorkspaceManager.close_project()
        ws = WorkspaceManager.open_project("alpha")
        self.assertEqual(ws.name, "alpha")
        active = WorkspaceManager.get_active()
        self.assertEqual(active.name, "alpha")


if __name__ == "__main__":
    unittest.main(verbosity=2)

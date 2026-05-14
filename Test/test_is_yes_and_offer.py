"""
Test automatici per is_yes e offer_open_folder.
Eseguire con: venv\Scripts\python.exe Test\test_is_yes_and_offer.py
"""
import sys, json, types, unittest
sys.path.insert(0, "D:/RecordingStudio/DubbingToolkit")

from unittest.mock import patch, MagicMock
from core.input_parsing import is_yes
from core.ui_printer import offer_open_folder

def make_messages(lang):
    with open(f"D:/RecordingStudio/DubbingToolkit/locale/Active/{lang}.json", encoding="utf-8") as f:
        return types.SimpleNamespace(**json.load(f))

IT = make_messages("it")
EN = make_messages("en")


class TestIsYes(unittest.TestCase):

    def test_it_yes(self):
        for v in ("s", "S", "si", "Si"):
            self.assertTrue(is_yes(v, IT), f"IT: {v!r} dovrebbe essere True")

    def test_it_no(self):
        for v in ("n", "no", "y", "yes", ""):
            self.assertFalse(is_yes(v, IT), f"IT: {v!r} dovrebbe essere False")

    def test_en_yes(self):
        for v in ("y", "Y", "yes", "Yes"):
            self.assertTrue(is_yes(v, EN), f"EN: {v!r} dovrebbe essere True")

    def test_en_no(self):
        for v in ("n", "no", "s", "si", ""):
            self.assertFalse(is_yes(v, EN), f"EN: {v!r} dovrebbe essere False")


class TestOfferOpenFolder(unittest.TestCase):

    def test_it_yes_opens_folder(self):
        with patch("builtins.input", return_value="s"), \
             patch("os.startfile") as mock_sf:
            offer_open_folder("/fake/path", IT)
        self.assertTrue(mock_sf.called, "IT 's': os.startfile dovrebbe essere chiamato")

    def test_it_no_does_not_open(self):
        with patch("builtins.input", return_value="n"), \
             patch("os.startfile") as mock_sf:
            offer_open_folder("/fake/path", IT)
        self.assertFalse(mock_sf.called, "IT 'n': os.startfile NON dovrebbe essere chiamato")

    def test_en_yes_opens_folder(self):
        with patch("builtins.input", return_value="y"), \
             patch("os.startfile") as mock_sf:
            offer_open_folder("/fake/path", EN)
        self.assertTrue(mock_sf.called, "EN 'y': os.startfile dovrebbe essere chiamato")

    def test_en_no_does_not_open(self):
        with patch("builtins.input", return_value="n"), \
             patch("os.startfile") as mock_sf:
            offer_open_folder("/fake/path", EN)
        self.assertFalse(mock_sf.called, "EN 'n': os.startfile NON dovrebbe essere chiamato")


if __name__ == "__main__":
    unittest.main(verbosity=2)

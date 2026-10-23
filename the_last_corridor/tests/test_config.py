"""
Testes Unitários de Configuração e Serialização JSON de THE LAST CORRIDOR.
"""

import unittest
import tempfile
from pathlib import Path
from the_last_corridor.core.config import GameConfig
from the_last_corridor.core.save_manager import SaveManager


class TestConfig(unittest.TestCase):
    def test_default_config_values(self):
        cfg = GameConfig()
        self.assertEqual(cfg.display.width, 1024)
        self.assertEqual(cfg.display.height, 768)
        self.assertEqual(cfg.desktop.computer_name, "ARCHIVE-09")
        self.assertIn("Meus Documentos/Pessoal/nao_abra", cfg.dangerous_folders)

    def test_to_dict_and_from_dict(self):
        cfg = GameConfig()
        cfg.maze.cols = 25
        cfg.investigation.secret_code = "TESTE-99"

        d = cfg.to_dict()
        self.assertEqual(d["maze"]["cols"], 25)
        self.assertEqual(d["investigation"]["secret_code"], "TESTE-99")

        new_cfg = GameConfig()
        new_cfg.from_dict(d)
        self.assertEqual(new_cfg.maze.cols, 25)
        self.assertEqual(new_cfg.investigation.secret_code, "TESTE-99")

    def test_save_and_load_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / "test_profile.json"
            cfg = GameConfig()
            cfg.desktop.computer_name = "TERMINAL-1998"
            cfg.save_to_file(tmp_path)

            loaded = GameConfig.load_from_file(tmp_path)
            self.assertEqual(loaded.desktop.computer_name, "TERMINAL-1998")


if __name__ == "__main__":
    unittest.main()

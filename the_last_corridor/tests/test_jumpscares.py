"""
Testes Unitários do Controlador de Jumpscares e Pastas Perigosas em THE LAST CORRIDOR.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
import pygame
from the_last_corridor.core.config import FinalJumpscareConfig, DangerousFolderConfig
from the_last_corridor.core.asset_manager import AssetManager
from the_last_corridor.core.audio_manager import AudioManager
from the_last_corridor.game.jumpscare import JumpscareController


class TestJumpscares(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.asset_mgr = AssetManager()
        self.audio_mgr = AudioManager()
        self.config = FinalJumpscareConfig(duration_ms=500, screen_shake=True, zoom=True)
        self.controller = JumpscareController(
            config=self.config,
            asset_manager=self.asset_mgr,
            audio_manager=self.audio_mgr
        )

    def test_jumpscare_lifecycle(self):
        self.assertFalse(self.controller.is_active)
        self.controller.trigger()
        self.assertTrue(self.controller.is_active)
        self.assertFalse(self.controller.has_finished)

    def test_dangerous_folder_config(self):
        folder_cfg = DangerousFolderConfig(
            folder_path="Meus Documentos/Pessoal/nao_abra",
            status="dangerous",
            duration_ms=1800,
            shake=True,
            trigger_once=True
        )
        self.assertEqual(folder_cfg.status, "dangerous")
        self.assertTrue(folder_cfg.shake)
        self.assertFalse(folder_cfg.has_triggered)


if __name__ == "__main__":
    unittest.main()

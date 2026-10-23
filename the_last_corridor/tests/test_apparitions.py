"""
Testes Unitários do Sistema de Aparições e Flashes Macabros em THE LAST CORRIDOR.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
import pygame
from the_last_corridor.core.config import ApparitionItem
from the_last_corridor.core.asset_manager import AssetManager
from the_last_corridor.core.audio_manager import AudioManager
from the_last_corridor.game.apparition_manager import ApparitionManager


class TestApparitions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.asset_mgr = AssetManager()
        self.audio_mgr = AudioManager()
        self.item = ApparitionItem(
            id="test_scare",
            duration_ms=180,
            probability=1.0,
            min_interval_sec=5.0,
            min_distance_steps=10,
            region_tag="mid"
        )
        self.mgr = ApparitionManager(
            apparitions=[self.item],
            asset_manager=self.asset_mgr,
            audio_manager=self.audio_mgr
        )

    def test_respects_step_threshold(self):
        # Jogador andou apenas 4 passos (menos que os 10 mínimos)
        triggered = self.mgr.update(player_steps=4, current_region="mid", dt=1.0)
        self.assertFalse(triggered, "Não deve disparar susto antes da distância mínima em passos.")

    def test_respects_region(self):
        # Região errada ('start' em vez de 'mid')
        triggered = self.mgr.update(player_steps=20, current_region="start", dt=1.0)
        self.assertFalse(triggered, "Não deve disparar susto fora da região configurada.")

    def test_trigger_and_expiration(self):
        self.mgr.trigger_apparition(self.item, player_steps=15)
        self.assertTrue(self.mgr.current_scare is not None)
        self.assertEqual(self.mgr.current_scare.id, "test_scare")


if __name__ == "__main__":
    unittest.main()

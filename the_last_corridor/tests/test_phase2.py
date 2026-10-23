"""
Testes Unitários da Segunda Fase (Inimigos, Orbe e Transições).
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
import pygame
from the_last_corridor.game.maze import Maze
from the_last_corridor.game.player import Player
from the_last_corridor.game.enemy import Enemy, EnemyManager
from the_last_corridor.game.orb import MysteriousOrb
from the_last_corridor.core.audio_manager import AudioManager


class TestPhase2Features(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

    def setUp(self):
        self.audio = AudioManager()
        self.maze = Maze(cols=19, rows=19, cell_size=40)

    def test_enemy_spawning_and_count(self):
        """Verifica se os inimigos são gerados corretamente no labirinto."""
        em = EnemyManager(self.maze, count=3)
        self.assertEqual(len(em.enemies), 3)
        for enemy in em.enemies:
            self.assertTrue(enemy.is_alive)
            self.assertFalse(enemy.caught_player)

    def test_enemy_chase_detection(self):
        """Verifica se o inimigo detecta o jogador e entra em estado de perseguição."""
        enemy = Enemy(x=100.0, y=100.0, speed=2.0, detection_radius=150.0)
        enemy.update(player_x=120.0, player_y=100.0, maze=self.maze, dt=0.016)
        self.assertEqual(enemy.state, Enemy.CHASE)

    def test_orb_interaction_and_collection(self):
        """Verifica o comportamento de proximidade e coleta da orbe misteriosa."""
        orb = MysteriousOrb(x=200.0, y=200.0, audio_manager=self.audio)
        self.assertFalse(orb.collected)
        
        # Longe da orbe
        orb.update(player_x=50.0, player_y=50.0, dt=0.016)
        self.assertFalse(orb.highlight)
        self.assertFalse(orb.try_collect(player_x=50.0, player_y=50.0))
        
        # Perto da orbe
        orb.update(player_x=210.0, player_y=200.0, dt=0.016)
        self.assertTrue(orb.highlight)
        collected = orb.try_collect(player_x=210.0, player_y=200.0)
        self.assertTrue(collected)
        self.assertTrue(orb.collected)

    def test_maze_open_cells(self):
        """Verifica se get_open_cells retorna células livres válidas."""
        cells = self.maze.get_open_cells()
        self.assertGreater(len(cells), 10)
        for cx, cy in cells:
            self.assertFalse(self.maze.is_wall(cx, cy))


if __name__ == "__main__":
    unittest.main()

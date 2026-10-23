"""
Testes Unitários do Módulo de Labirinto de THE LAST CORRIDOR.
"""

import unittest
from the_last_corridor.game.maze import Maze


class TestMaze(unittest.TestCase):
    def test_maze_dimensions(self):
        m = Maze(cols=19, rows=19, cell_size=40)
        self.assertEqual(m.cols, 19)
        self.assertEqual(m.rows, 19)
        self.assertEqual(len(m.grid), 19)
        self.assertEqual(len(m.grid[0]), 19)

    def test_start_and_exit_are_open(self):
        m = Maze(cols=15, rows=15)
        sx, sy = m.start_pos
        ex, ey = m.exit_pos
        self.assertEqual(m.grid[sy][sx], 0, "O ponto de início deve ser um caminho aberto (0)")
        self.assertEqual(m.grid[ey][ex], 0, "O ponto de saída deve ser um caminho aberto (0)")

    def test_boundaries_are_walls(self):
        m = Maze(cols=15, rows=15)
        # As bordas externas devem ser paredes
        for x in range(m.cols):
            self.assertTrue(m.is_wall(x, 0))
            self.assertTrue(m.is_wall(x, m.rows - 1))
        for y in range(m.rows):
            self.assertTrue(m.is_wall(0, y))
            self.assertTrue(m.is_wall(m.cols - 1, y))

    def test_region_tags(self):
        m = Maze(cols=21, rows=21)
        sx, sy = m.start_pos
        ex, ey = m.exit_pos
        self.assertEqual(m.get_region_tag(sx, sy), "start")
        self.assertEqual(m.get_region_tag(ex, ey), "near_exit")
        self.assertEqual(m.get_region_tag(10, 10), "mid")


if __name__ == "__main__":
    unittest.main()

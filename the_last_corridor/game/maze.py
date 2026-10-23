"""
Módulo de Geração e Gerenciamento do Labirinto de THE LAST CORRIDOR.
Gera labirintos 2D com garantia de caminho entre início e saída usando DFS Recursive Backtracker.
"""

import random
from typing import List, Tuple, Dict, Any


class Maze:
    def __init__(self, cols: int = 19, rows: int = 19, cell_size: int = 40):
        self.cols = cols if cols % 2 != 0 else cols + 1
        self.rows = rows if rows % 2 != 0 else rows + 1
        self.cell_size = cell_size

        # 1 = Parede, 0 = Caminho livre
        self.grid: List[List[int]] = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        self.start_pos: Tuple[int, int] = (1, 1)
        self.exit_pos: Tuple[int, int] = (self.cols - 2, self.rows - 2)

        self.generate()

    def generate(self):
        """Gera um labirinto perfeito usando o algoritmo de backtracking recursivo."""
        self.grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        stack = [self.start_pos]
        self.grid[self.start_pos[1]][self.start_pos[0]] = 0

        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]

        while stack:
            cx, cy = stack[-1]
            neighbors = []

            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < self.cols - 1 and 0 < ny < self.rows - 1 and self.grid[ny][nx] == 1:
                    neighbors.append((nx, ny, dx, dy))

            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                # Remove a parede intermediária
                self.grid[cy + dy // 2][cx + dx // 2] = 0
                self.grid[ny][nx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()

        # Garante a abertura da saída
        ex, ey = self.exit_pos
        self.grid[ey][ex] = 0

        # Cria caminhos alternativos e loops para fuga de monstros (não ser um beco sem saída rígido)
        self._carve_loops()

    def _carve_loops(self):
        """Remove seletivamente algumas paredes internas para criar bifurcações e rotas de fuga."""
        removable_walls = []
        for r in range(2, self.rows - 2):
            for c in range(2, self.cols - 2):
                if self.grid[r][c] == 1:
                    # Parede horizontal entre dois caminhos livres
                    if self.grid[r - 1][c] == 0 and self.grid[r + 1][c] == 0 and self.grid[r][c - 1] == 1 and self.grid[r][c + 1] == 1:
                        removable_walls.append((c, r))
                    # Parede vertical entre dois caminhos livres
                    elif self.grid[r][c - 1] == 0 and self.grid[r][c + 1] == 0 and self.grid[r - 1][c] == 1 and self.grid[r + 1][c] == 1:
                        removable_walls.append((c, r))

        # Remove cerca de 28% dessas paredes para abrir anéis de fuga fluídos
        if removable_walls:
            num_to_remove = max(4, int(len(removable_walls) * 0.28))
            chosen = random.sample(removable_walls, min(num_to_remove, len(removable_walls)))
            for cx, cy in chosen:
                self.grid[cy][cx] = 0

    def is_wall(self, grid_x: int, grid_y: int) -> bool:
        """Verifica se as coordenadas de grade são uma parede ou estão fora dos limites."""
        if grid_x < 0 or grid_x >= self.cols or grid_y < 0 or grid_y >= self.rows:
            return True
        return self.grid[grid_y][grid_x] == 1

    def get_world_pos(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Converte coordenadas da grade em pixels (centro da célula)."""
        return (grid_x + 0.5) * self.cell_size, (grid_y + 0.5) * self.cell_size

    def get_region_tag(self, grid_x: int, grid_y: int) -> str:
        """Determina a região do labirinto (start, mid, near_exit)."""
        dist_to_start = abs(grid_x - self.start_pos[0]) + abs(grid_y - self.start_pos[1])
        dist_to_exit = abs(grid_x - self.exit_pos[0]) + abs(grid_y - self.exit_pos[1])

        if dist_to_exit <= 4:
            return "near_exit"
        elif dist_to_start <= 4:
            return "start"
        else:
            return "mid"

    def get_open_cells(self) -> List[Tuple[int, int]]:
        """Retorna lista de (grid_x, grid_y) de todas as células livres (não paredes)."""
        cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == 0:
                    cells.append((c, r))
        return cells

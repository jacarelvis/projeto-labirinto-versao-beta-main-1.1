"""
Sistema de Detecção e Resolução de Colisões do Labirinto.
Permite deslizamento suave pelas paredes para garantir controles responsivos e sem travamento.
"""

import pygame
from typing import Tuple
from .maze import Maze


class CollisionSystem:
    @staticmethod
    def move_and_collide(
        x: float, y: float, dx: float, dy: float, radius: float, maze: Maze
    ) -> Tuple[float, float, bool]:
        """
        Move a entidade aplicando colisão independente por eixo (X e Y)
        para permitir deslizamento contínuo contra as paredes.
        Retorna (novo_x, novo_y, colidiu).
        """
        collided = False

        # 1. Movimento no eixo X
        new_x = x + dx
        if CollisionSystem._check_collision(new_x, y, radius, maze):
            new_x = x
            collided = True

        # 2. Movimento no eixo Y
        new_y = y + dy
        if CollisionSystem._check_collision(new_x, new_y, radius, maze):
            new_y = y
            collided = True

        return new_x, new_y, collided

    @staticmethod
    def _check_collision(x: float, y: float, radius: float, maze: Maze) -> bool:
        """Verifica se o círculo do jogador colide com qualquer ladrilho sólido ao redor."""
        cs = maze.cell_size

        min_gx = int((x - radius) // cs)
        max_gx = int((x + radius) // cs)
        min_gy = int((y - radius) // cs)
        max_gy = int((y + radius) // cs)

        for gy in range(min_gy, max_gy + 1):
            for gx in range(min_gx, max_gx + 1):
                if maze.is_wall(gx, gy):
                    # Retângulo da parede
                    rect_x = gx * cs
                    rect_y = gy * cs

                    # Ponto mais próximo do retângulo ao centro do círculo
                    closest_x = max(rect_x, min(x, rect_x + cs))
                    closest_y = max(rect_y, min(y, rect_y + cs))

                    dist_x = x - closest_x
                    dist_y = y - closest_y

                    if (dist_x * dist_x + dist_y * dist_y) < (radius * radius):
                        return True
        return False

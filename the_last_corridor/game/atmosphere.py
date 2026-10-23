"""
Atmosfera e Iluminação Claustrofóbica do Labirinto de THE LAST CORRIDOR.
Cria iluminação de lanterna dinâmica com oscilação sutil, escuridão densa e câmera centralizada.
"""

import pygame
import math
import random
from typing import Tuple
from .maze import Maze


class AtmosphereRenderer:
    def __init__(self, screen_w: int, screen_h: int, base_radius: int = 140):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.base_radius = base_radius
        self.darkness_surface = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        self.flicker_phase: float = 0.0

        # Textura do chão e parede pré-renderizada para alta performance
        self.floor_color = (8, 12, 18)
        self.wall_color = (20, 26, 36)
        self.wall_border_color = (35, 45, 62)

    def update_size(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.darkness_surface = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)

    def get_camera_offset(self, player_x: float, player_y: float) -> Tuple[float, float]:
        """Calcula o deslocamento da câmera para manter o jogador no centro da tela."""
        cam_x = player_x - self.screen_w / 2
        cam_y = player_y - self.screen_h / 2
        return cam_x, cam_y

    def render_maze(self, surface: pygame.Surface, maze: Maze, cam_offset: Tuple[float, float]):
        """Desenha o labirinto (chão, paredes e portal de saída)."""
        cs = maze.cell_size
        cam_x, cam_y = cam_offset

        # Determina o intervalo visível de blocos para otimizar renderização
        min_gx = max(0, int(cam_x // cs) - 1)
        max_gx = min(maze.cols, int((cam_x + self.screen_w) // cs) + 2)
        min_gy = max(0, int(cam_y // cs) - 1)
        max_gy = min(maze.rows, int((cam_y + self.screen_h) // cs) + 2)

        for gy in range(min_gy, max_gy):
            for gx in range(min_gx, max_gx):
                px = int(gx * cs - cam_x)
                py = int(gy * cs - cam_y)

                if maze.grid[gy][gx] == 1:
                    # Parede com relevo sutil
                    pygame.draw.rect(surface, self.wall_color, (px, py, cs, cs))
                    pygame.draw.rect(surface, self.wall_border_color, (px, py, cs, cs), 1)
                else:
                    # Corredor
                    pygame.draw.rect(surface, self.floor_color, (px, py, cs, cs))

        # Desenhar Saída Ominosa (o ponto que atrai o jogador)
        ex, ey = maze.exit_pos
        exit_px = int(ex * cs - cam_x)
        exit_py = int(ey * cs - cam_y)

        # Luz convidativa da "saída"
        glow_pulse = math.sin(pygame.time.get_ticks() / 250) * 0.2 + 0.8
        glow_radius = int(cs * 0.65 * glow_pulse)
        center_x = exit_px + cs // 2
        center_y = exit_py + cs // 2

        pygame.draw.circle(surface, (168, 85, 247), (center_x, center_y), glow_radius)
        pygame.draw.circle(surface, (236, 72, 153), (center_x, center_y), int(cs * 0.35))
        pygame.draw.rect(surface, (255, 255, 255), (center_x - 4, center_y - 8, 8, 16))

    def render_flashlight_and_darkness(
        self,
        surface: pygame.Surface,
        player_screen_x: int,
        player_screen_y: int,
        reduce_flashes: bool = False
    ):
        """Aplica escuridão total e corta um círculo de visão ao redor do jogador."""
        self.darkness_surface.fill((2, 4, 8, 250))

        # Oscilação sutil da lanterna
        if not reduce_flashes:
            self.flicker_phase += 0.05
            flicker = math.sin(self.flicker_phase) * 5 + (random.random() - 0.5) * 3
        else:
            flicker = 0

        current_radius = max(60, int(self.base_radius + flicker))

        # Desenhar anéis gradientes concêntricos com alpha decrescente (visão de lanterna)
        steps = 14
        for i in range(steps):
            r = int(current_radius * (1.0 - i / steps))
            alpha = int(250 * (i / steps))
            if r > 0:
                # Usa blend SUB ou preenchimento de corte
                pygame.draw.circle(
                    self.darkness_surface,
                    (2, 4, 8, alpha),
                    (player_screen_x, player_screen_y),
                    r
                )

        # Recorte suave do centro
        pygame.draw.circle(
            self.darkness_surface,
            (2, 4, 8, 0),
            (player_screen_x, player_screen_y),
            int(current_radius * 0.35)
        )

        surface.blit(self.darkness_surface, (0, 0))

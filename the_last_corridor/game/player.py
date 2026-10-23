"""
Entidade do Jogador de THE LAST CORRIDOR.
Gerencia movimentação fluida (WASD e Setas), colisão com deslizamento e registro de passos.
"""

import pygame
import math
from typing import Tuple
try:
    from game.maze import Maze
    from game.collision import CollisionSystem
    from core.audio_manager import AudioManager
except ImportError:
    from the_last_corridor.game.maze import Maze
    from the_last_corridor.game.collision import CollisionSystem
    from the_last_corridor.core.audio_manager import AudioManager


class Player:
    def __init__(self, x: float, y: float, speed: float = 4.0, radius: float = 12.0):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius

        # Rastreamento de passos para aparições e áudio
        self.total_distance: float = 0.0
        self.step_accumulator: float = 0.0
        self.steps_count: int = 0
        self.facing_angle: float = 0.0
        self.is_moving: bool = False

    def handle_input(self, keys, maze: Maze, audio: AudioManager, dt: float = 1.0):
        """Processa entrada do teclado (WASD / Setas) e move o jogador."""
        dx, dy = 0.0, 0.0

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1.0

        if dx != 0.0 or dy != 0.0:
            # Normalização para evitar velocidade diagonal excessiva
            length = math.hypot(dx, dy)
            dx = (dx / length) * self.speed * dt
            dy = (dy / length) * self.speed * dt

            self.facing_angle = math.atan2(dy, dx)
            new_x, new_y, collided = CollisionSystem.move_and_collide(
                self.x, self.y, dx, dy, self.radius, maze
            )

            actual_dist = math.hypot(new_x - self.x, new_y - self.y)
            self.x = new_x
            self.y = new_y
            self.is_moving = actual_dist > 0.1

            if self.is_moving:
                self.total_distance += actual_dist
                self.step_accumulator += actual_dist

                # Som de passos e contagem a cada ~28 pixels
                step_threshold = maze.cell_size * 0.7
                if self.step_accumulator >= step_threshold:
                    self.step_accumulator -= step_threshold
                    self.steps_count += 1
                    audio.play_footstep()
        else:
            self.is_moving = False

    def get_grid_pos(self, cell_size: int) -> Tuple[int, int]:
        """Retorna as coordenadas da célula atual no labirinto."""
        return int(self.x // cell_size), int(self.y // cell_size)

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        """Renderiza o jogador com um indicador de direção e brilho sutil."""
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        # Corpo do jogador (circulo escuro azulado com borda ciano)
        pygame.draw.circle(surface, (15, 23, 42), (screen_x, screen_y), int(self.radius))
        pygame.draw.circle(surface, (56, 189, 248), (screen_x, screen_y), int(self.radius), 2)

        # Lanterna frontal / indicador de direção
        beam_len = self.radius + 6
        end_x = screen_x + math.cos(self.facing_angle) * beam_len
        end_y = screen_y + math.sin(self.facing_angle) * beam_len
        pygame.draw.line(surface, (254, 240, 138), (screen_x, screen_y), (int(end_x), int(end_y)), 3)

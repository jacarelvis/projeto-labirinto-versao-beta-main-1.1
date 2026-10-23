"""
Sistema de Inimigos para a Segunda Fase de THE LAST CORRIDOR.
Inimigos patrulham o labirinto e perseguem o jogador quando próximos.
"""
import pygame
import math
import random
from typing import Tuple, List, Optional

try:
    from game.maze import Maze
    from game.collision import CollisionSystem
except ImportError:
    from the_last_corridor.game.maze import Maze
    from the_last_corridor.game.collision import CollisionSystem


class Enemy:
    """Inimigo que patrulha o labirinto e persegue o jogador."""
    
    PATROL = "patrol"
    CHASE = "chase"
    
    def __init__(self, x: float, y: float, speed: float = 2.2, detection_radius: float = 160.0):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = 14.0
        self.detection_radius = detection_radius
        self.state = self.PATROL
        
        # Patrulha
        self.patrol_points: List[Tuple[float, float]] = []
        self.patrol_index = 0
        self.patrol_wait = 0.0
        
        # Perseguição
        self.chase_speed = speed * 1.6
        self.lose_player_timer = 0.0
        
        # Visual
        self.pulse_timer = 0.0
        self.color = (190, 15, 25)
        self.eye_color = (255, 230, 80)
        
        # Estado
        self.is_alive = True
        self.caught_player = False
        
        # Direção
        self.facing_angle = 0.0
    
    def set_patrol_points(self, points: List[Tuple[float, float]]):
        self.patrol_points = points
        self.patrol_index = 0
    
    def update(self, player_x: float, player_y: float, maze: Maze, dt: float):
        """Atualiza a lógica e o comportamento do inimigo."""
        if not self.is_alive:
            return
        
        self.pulse_timer += dt * 3.0
        dist_to_player = math.hypot(player_x - self.x, player_y - self.y)
        
        if dist_to_player < self.detection_radius:
            self.state = self.CHASE
            self.lose_player_timer = 3.0
        elif self.state == self.CHASE:
            self.lose_player_timer -= dt
            if self.lose_player_timer <= 0:
                self.state = self.PATROL
        
        if self.state == self.CHASE:
            self._move_towards(player_x, player_y, self.chase_speed, maze, dt)
        elif self.state == self.PATROL and self.patrol_points:
            self._patrol(maze, dt)
        
        # Colisão fatal com o jogador
        if dist_to_player < self.radius + 12.0:
            self.caught_player = True
    
    def _move_towards(self, tx: float, ty: float, speed: float, maze: Maze, dt: float):
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist < 1.0:
            return
        dx /= dist
        dy /= dist
        self.facing_angle = math.atan2(dy, dx)
        step = speed * dt * 60.0
        new_x, new_y, _ = CollisionSystem.move_and_collide(
            self.x, self.y, dx * step, dy * step, self.radius, maze
        )
        self.x = new_x
        self.y = new_y
    
    def _patrol(self, maze: Maze, dt: float):
        if not self.patrol_points:
            return
        
        if self.patrol_wait > 0:
            self.patrol_wait -= dt
            return
        
        tx, ty = self.patrol_points[self.patrol_index]
        dist = math.hypot(tx - self.x, ty - self.y)
        
        if dist < 12.0:
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
            self.patrol_wait = random.uniform(0.4, 1.2)
        else:
            self._move_towards(tx, ty, self.speed, maze, dt)
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        if not self.is_alive:
            return
        
        sx = int(self.x - camera_offset[0])
        sy = int(self.y - camera_offset[1])
        
        pulse = 0.85 + 0.15 * math.sin(self.pulse_timer)
        r = int(self.radius * pulse)
        
        # Aura escura avermelhada
        aura_surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        alpha = int(70 + 40 * math.sin(self.pulse_timer * 2))
        pygame.draw.circle(aura_surf, (180, 0, 0, alpha), (r * 2, r * 2), r * 2)
        surface.blit(aura_surf, (sx - r * 2, sy - r * 2))
        
        # Corpo
        pygame.draw.circle(surface, (10, 0, 0), (sx, sy), r + 2)
        pygame.draw.circle(surface, self.color, (sx, sy), r)
        
        # Olhos brilhantes que encaram na direção de movimento
        ex1 = sx + int(math.cos(self.facing_angle - 0.4) * r * 0.5)
        ey1 = sy + int(math.sin(self.facing_angle - 0.4) * r * 0.5)
        ex2 = sx + int(math.cos(self.facing_angle + 0.4) * r * 0.5)
        ey2 = sy + int(math.sin(self.facing_angle + 0.4) * r * 0.5)
        pygame.draw.circle(surface, self.eye_color, (ex1, ey1), 3)
        pygame.draw.circle(surface, self.eye_color, (ex2, ey2), 3)
        
        # Indicador de alerta de perseguição
        if self.state == self.CHASE:
            pygame.draw.circle(surface, (255, 30, 0), (sx, sy), r + 4, 2)


class EnemyManager:
    """Gerencia a patrulha e caça dos inimigos no labirinto."""
    
    def __init__(self, maze: Maze, count: int = 3):
        self.enemies: List[Enemy] = []
        self.maze = maze
        self._spawn_enemies(count)
        self.any_caught = False
    
    def _spawn_enemies(self, count: int):
        cells = self.maze.get_open_cells()
        sx, sy = self.maze.start_pos
        # Não spawnar perto da entrada inicial
        valid_cells = [(cx, cy) for cx, cy in cells if math.hypot(cx - sx, cy - sy) > 6]
        if not valid_cells:
            valid_cells = cells
        
        random.shuffle(valid_cells)
        used = valid_cells[:count]
        
        for i, (cx, cy) in enumerate(used):
            px, py = self.maze.get_world_pos(cx, cy)
            enemy = Enemy(px, py, speed=1.8 + i * 0.25, detection_radius=145.0 + i * 20.0)
            
            # 3 a 5 pontos de patrulha
            patrol_cells = random.sample(valid_cells, min(4, len(valid_cells)))
            patrol_pts = [self.maze.get_world_pos(c[0], c[1]) for c in patrol_cells]
            enemy.set_patrol_points(patrol_pts)
            self.enemies.append(enemy)
    
    def update(self, player_x: float, player_y: float, dt: float) -> bool:
        """Atualiza todos os inimigos. Retorna True se o jogador foi pego."""
        for enemy in self.enemies:
            enemy.update(player_x, player_y, self.maze, dt)
            if enemy.caught_player:
                self.any_caught = True
                return True
        return False
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        for enemy in self.enemies:
            enemy.draw(surface, camera_offset)
    
    def reset_caught(self):
        for enemy in self.enemies:
            enemy.caught_player = False
        self.any_caught = False

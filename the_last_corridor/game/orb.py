"""
Orbe Misteriosa da Segunda Fase de THE LAST CORRIDOR.
Objeto sobrenatural flutuante que dispara o jumpscare da orbe ao ser coletada.
"""
import pygame
import math
import random
from typing import Tuple

try:
    from core.audio_manager import AudioManager
except ImportError:
    from the_last_corridor.core.audio_manager import AudioManager


class MysteriousOrb:
    def __init__(self, x: float, y: float, audio_manager: AudioManager):
        self.x = x
        self.y = y
        self.radius = 18.0
        self.interact_radius = 58.0
        self.audio_manager = audio_manager
        
        self.collected = False
        self.pulse_timer = 0.0
        self.float_timer = 0.0
        self.particles = []
        self.highlight = False
        self._init_particles()
    
    def _init_particles(self):
        for _ in range(16):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(18, 48)
            speed = random.uniform(0.4, 1.2)
            self.particles.append({
                'angle': angle,
                'dist': dist,
                'speed': speed,
                'size': random.randint(2, 4),
                'alpha': random.randint(110, 220)
            })
    
    def update(self, player_x: float, player_y: float, dt: float):
        if self.collected:
            return
        
        self.pulse_timer += dt * 2.8
        self.float_timer += dt * 1.5
        
        for p in self.particles:
            p['angle'] += p['speed'] * dt
        
        dist = math.hypot(player_x - self.x, player_y - self.y)
        self.highlight = dist < self.interact_radius
    
    def try_collect(self, player_x: float, player_y: float) -> bool:
        """Tenta interagir e pegar a orbe."""
        if self.collected:
            return False
        dist = math.hypot(player_x - self.x, player_y - self.y)
        if dist < self.interact_radius:
            self.collected = True
            return True
        return False
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        if self.collected:
            return
        
        sx = int(self.x - camera_offset[0])
        sy_base = int(self.y - camera_offset[1])
        float_offset = int(math.sin(self.float_timer) * 7.0)
        sy = sy_base + float_offset
        
        pulse = 0.85 + 0.15 * math.sin(self.pulse_timer)
        r = int(self.radius * pulse)
        
        # Partículas orbitais
        part_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        for p in self.particles:
            px = sx + int(math.cos(p['angle']) * p['dist'])
            py = sy + int(math.sin(p['angle']) * (p['dist'] * 0.55))
            alpha = int(p['alpha'] * pulse)
            pygame.draw.circle(part_surf, (160, 100, 255, alpha), (px, py), p['size'])
        surface.blit(part_surf, (0, 0))
        
        # Aura roxa sobrenatural
        aura_r = r + 22
        aura = pygame.Surface((aura_r * 2 + 2, aura_r * 2 + 2), pygame.SRCALPHA)
        aura_alpha = int(70 * pulse)
        pygame.draw.circle(aura, (140, 50, 240, aura_alpha), (aura_r + 1, aura_r + 1), aura_r)
        surface.blit(aura, (sx - aura_r, sy - aura_r))
        
        # Núcleo da orbe
        pygame.draw.circle(surface, (25, 5, 50), (sx, sy), r + 2)
        core_color = (220, 180, 255) if self.highlight else (190, 140, 245)
        pygame.draw.circle(surface, core_color, (sx, sy), r)
        
        # Brilho central
        inner_r = max(4, r // 2)
        pygame.draw.circle(surface, (255, 240, 255), (sx, sy), inner_r)
        
        # Aviso de interação ao aproximar
        if self.highlight:
            pygame.draw.circle(surface, (255, 255, 180), (sx, sy), r + 4, 2)
            try:
                font = pygame.font.SysFont("Courier New", 14, bold=True)
                txt = font.render("[E] PEGAR ORBE", True, (255, 255, 190))
                surface.blit(txt, (sx - txt.get_width() // 2, sy - r - 26))
            except Exception:
                pass

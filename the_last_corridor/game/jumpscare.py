"""
Controlador de Jumpscare Principal de THE LAST CORRIDOR.
Executa o susto final do labirinto com tremor de tela, zoom, flashes e distorção,
seguido de transição para o computador antigo simulado.
"""

import pygame
import time
import math
import random
from typing import Optional, Tuple
try:
    from core.config import FinalJumpscareConfig
    from core.asset_manager import AssetManager
    from core.audio_manager import AudioManager
except ImportError:
    from the_last_corridor.core.config import FinalJumpscareConfig
    from the_last_corridor.core.asset_manager import AssetManager
    from the_last_corridor.core.audio_manager import AudioManager


class JumpscareController:
    def __init__(
        self,
        config: FinalJumpscareConfig,
        asset_manager: AssetManager,
        audio_manager: AudioManager
    ):
        self.config = config
        self.asset_manager = asset_manager
        self.audio_manager = audio_manager

        self.is_active: bool = False
        self.has_finished: bool = False
        self.start_time: float = 0.0
        self.elapsed_ms: float = 0.0

    def trigger(self):
        """Dispara o susto principal."""
        self.is_active = True
        self.has_finished = False
        self.start_time = time.time()
        self.elapsed_ms = 0.0

        # Dispara o áudio estridente (interrompe o som ambiente)
        sound_type = getattr(self.config, "sound_type", "scream")
        self.audio_manager.play_jumpscare(
            path_str=self.config.sound_path,
            sound_type=sound_type,
            volume_mult=self.config.volume
        )

    def update(self) -> bool:
        """Atualiza o temporizador do susto. Retorna True enquanto estiver em andamento."""
        if not self.is_active:
            return False

        self.elapsed_ms = (time.time() - self.start_time) * 1000.0

        if self.elapsed_ms >= self.config.duration_ms:
            self.is_active = False
            self.has_finished = True
            return False

        return True

    def draw(
        self,
        surface: pygame.Surface,
        screen_w: int,
        screen_h: int,
        reduce_flashes: bool = False,
        reduce_shakes: bool = False
    ) -> Tuple[int, int]:
        """
        Renderiza o jumpscare com efeitos de tremor, zoom e distorção visual.
        Retorna o deslocamento da tela (shake_x, shake_y) para efeitos globais.
        """
        if not self.is_active:
            return 0, 0

        progress = min(1.0, self.elapsed_ms / max(100.0, self.config.duration_ms))

        # 1. Tremor de tela violento
        shake_x, shake_y = 0, 0
        if self.config.screen_shake and not reduce_shakes:
            intensity = int(32 * (1.0 - progress * 0.7))
            shake_x = random.randint(-intensity, intensity)
            shake_y = random.randint(-intensity, intensity)

        # 2. Zoom na face macabra
        scale_factor = 1.0
        if self.config.zoom:
            scale_factor = 1.0 + (progress * 0.45)

        target_w = int(screen_w * scale_factor)
        target_h = int(screen_h * scale_factor)

        # Carrega a imagem do jumpscare
        scare_img = self.asset_manager.load_image(
            self.config.image_path,
            target_size=(target_w, target_h),
            fallback_type="jumpscare"
        )

        draw_x = (screen_w - target_w) // 2 + shake_x
        draw_y = (screen_h - target_h) // 2 + shake_y

        surface.blit(scare_img, (draw_x, draw_y))

        # 3. Flash visual nos primeiros 150ms
        if self.config.flash and not reduce_flashes:
            if self.elapsed_ms < 140:
                flash_surf = pygame.Surface((screen_w, screen_h))
                flash_surf.fill((255, 255, 255))
                flash_surf.set_alpha(int(240 * (1.0 - self.elapsed_ms / 140)))
                surface.blit(flash_surf, (0, 0))
            elif random.random() < 0.15:
                # Flashes vermelhos estroboscópicos ocasionais
                red_surf = pygame.Surface((screen_w, screen_h))
                red_surf.fill((180, 0, 0))
                red_surf.set_alpha(110)
                surface.blit(red_surf, (0, 0))

        # 4. Distorção de linhas horizontais de TV estragada
        if self.config.visual_distortion and not reduce_flashes:
            for _ in range(5):
                slice_y = random.randint(0, screen_h - 20)
                slice_h = random.randint(4, 16)
                offset = random.randint(-25, 25)
                rect = pygame.Rect(0, slice_y, screen_w, slice_h)
                sub = surface.subsurface(rect).copy()
                surface.blit(sub, (offset, slice_y))

        return shake_x, shake_y

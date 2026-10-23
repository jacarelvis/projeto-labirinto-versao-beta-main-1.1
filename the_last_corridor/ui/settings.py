"""
Menu de Configurações e Acessibilidade de THE LAST CORRIDOR.
Controla volumes de áudio, tela cheia, linhas CRT e redução de flashes e tremores.
"""

import pygame
from typing import Callable
try:
    from core.config import GameConfig
    from core.audio_manager import AudioManager
except ImportError:
    from the_last_corridor.core.config import GameConfig
    from the_last_corridor.core.audio_manager import AudioManager


class SettingsMenu:
    def __init__(
        self,
        config: GameConfig,
        audio_manager: AudioManager,
        on_back: Callable[[], None],
        screen_w: int = 1024,
        screen_h: int = 768
    ):
        self.config = config
        self.audio_manager = audio_manager
        self.on_back = on_back
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.options = [
            "Volume Geral",
            "Volume dos Sustos",
            "Volume Sons Ambiente",
            "Silenciar Áudio",
            "Reduzir Flashes",
            "Reduzir Tremores",
            "Linhas CRT Retro",
            "Voltar"
        ]
        self.selected_idx = 0

        self.title_font = pygame.font.SysFont("Georgia", 30, bold=True)
        self.font = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.val_font = pygame.font.SysFont("Segoe UI", 14)
        self.warn_font = pygame.font.SysFont("Segoe UI", 11, bold=True)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_idx = (self.selected_idx - 1) % len(self.options)
                self.audio_manager.play_ui_sound("click")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_idx = (self.selected_idx + 1) % len(self.options)
                self.audio_manager.play_ui_sound("click")
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._modify_current(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._modify_current(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selected_idx == len(self.options) - 1:
                    self.audio_manager.play_ui_sound("click")
                    self.on_back()
                else:
                    self._modify_current(1)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            start_y = 180
            for idx in range(len(self.options)):
                rect = pygame.Rect(self.screen_w // 2 - 250, start_y + idx * 50, 500, 42)
                if rect.collidepoint(mx, my):
                    self.selected_idx = idx
                    if idx == len(self.options) - 1:
                        self.audio_manager.play_ui_sound("click")
                        self.on_back()
                    else:
                        self._modify_current(1)

    def _modify_current(self, direction: int):
        idx = self.selected_idx
        self.audio_manager.play_ui_sound("click")

        if idx == 0:  # Master Volume
            self.config.audio.master_volume = max(0.0, min(1.0, round(self.config.audio.master_volume + direction * 0.1, 2)))
        elif idx == 1:  # Jumpscare Volume
            self.config.audio.jumpscare_volume = max(0.0, min(1.0, round(self.config.audio.jumpscare_volume + direction * 0.1, 2)))
        elif idx == 2:  # Ambient Volume
            self.config.audio.ambient_volume = max(0.0, min(1.0, round(self.config.audio.ambient_volume + direction * 0.1, 2)))
        elif idx == 3:  # Silenciar Áudio
            self.config.audio.audio_muted = not self.config.audio.audio_muted
        elif idx == 4:  # Reduce Flashes
            self.config.display.reduce_flashes = not self.config.display.reduce_flashes
        elif idx == 5:  # Reduce Shakes
            self.config.display.reduce_shakes = not self.config.display.reduce_shakes
        elif idx == 6:  # CRT Scanlines
            self.config.display.crt_scanlines = not self.config.display.crt_scanlines

        # Atualizar volumes aplicados no mixer
        self.audio_manager.set_volumes(
            master=self.config.audio.master_volume,
            jumpscare=self.config.audio.jumpscare_volume,
            ambient=self.config.audio.ambient_volume,
            muted=self.config.audio.audio_muted
        )

    def draw(self, surface: pygame.Surface):
        surface.fill((8, 12, 20))

        # Título
        title_surf = self.title_font.render("CONFIGURAÇÕES E ACESSIBILIDADE", True, (244, 63, 94))
        surface.blit(title_surf, ((self.screen_w - title_surf.get_width()) // 2, 70))

        # Aviso sonoro de terror
        warn_box = pygame.Rect(self.screen_w // 2 - 270, 120, 540, 32)
        pygame.draw.rect(surface, (69, 10, 10), warn_box, border_radius=4)
        pygame.draw.rect(surface, (239, 68, 68), warn_box, 1, border_radius=4)
        warn_txt = self.warn_font.render("AVISO: ESTE JOGO CONTÉM SUSTOS SONOROS E VISUAIS REPENTINOS", True, (254, 202, 202))
        surface.blit(warn_txt, (warn_box.x + (warn_box.w - warn_txt.get_width()) // 2, warn_box.y + 8))

        start_y = 175
        for idx, opt in enumerate(self.options):
            is_sel = (idx == self.selected_idx)
            row_rect = pygame.Rect(self.screen_w // 2 - 250, start_y + idx * 48, 500, 40)

            bg_col = (30, 41, 59) if is_sel else (15, 23, 42)
            pygame.draw.rect(surface, bg_col, row_rect, border_radius=6)
            pygame.draw.rect(surface, (244, 63, 94) if is_sel else (51, 65, 85), row_rect, width=2 if is_sel else 1, border_radius=6)

            # Rótulo
            lbl_surf = self.font.render(opt, True, (255, 255, 255) if is_sel else (203, 213, 225))
            surface.blit(lbl_surf, (row_rect.x + 20, row_rect.y + 10))

            # Valor
            val_str = ""
            if idx == 0:
                val_str = f"{int(self.config.audio.master_volume * 100)}%"
            elif idx == 1:
                val_str = f"{int(self.config.audio.jumpscare_volume * 100)}%"
            elif idx == 2:
                val_str = f"{int(self.config.audio.ambient_volume * 100)}%"
            elif idx == 3:
                val_str = "MUTADO" if self.config.audio.audio_muted else "NORMAL"
            elif idx == 4:
                val_str = "SIM" if self.config.display.reduce_flashes else "NÃO"
            elif idx == 5:
                val_str = "SIM" if self.config.display.reduce_shakes else "NÃO"
            elif idx == 6:
                val_str = "SIM" if self.config.display.crt_scanlines else "NÃO"

            if val_str:
                val_surf = self.val_font.render(f"◀ {val_str} ▶", True, (56, 189, 248) if is_sel else (148, 163, 184))
                surface.blit(val_surf, (row_rect.right - val_surf.get_width() - 20, row_rect.y + 10))

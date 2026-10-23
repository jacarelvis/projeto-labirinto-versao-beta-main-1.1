"""
Menu Principal de THE LAST CORRIDOR.
Apresenta opções: JOGAR, CONTINUAR, CONFIGURAÇÕES, PERSONALIZAR JOGO, TESTAR JUMPSCARES e SAIR.
"""

import pygame
import math
from typing import List, Tuple, Optional, Callable
try:
    from core.audio_manager import AudioManager
except ImportError:
    from the_last_corridor.core.audio_manager import AudioManager


class MainMenu:
    def __init__(
        self,
        audio_manager: AudioManager,
        on_play: Callable[[], None],
        on_continue: Callable[[], None],
        on_settings: Callable[[], None],
        on_customize: Callable[[], None],
        on_test_jumpscare: Callable[[], None],
        on_exit: Callable[[], None],
        has_save_game: bool = False,
        screen_w: int = 1024,
        screen_h: int = 768
    ):
        self.audio_manager = audio_manager
        self.on_play = on_play
        self.on_continue = on_continue
        self.on_settings = on_settings
        self.on_customize = on_customize
        self.on_test_jumpscare = on_test_jumpscare
        self.on_exit = on_exit
        self.has_save_game = has_save_game
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.options = [
            ("JOGAR", self.on_play, True),
            ("CONTINUAR", self.on_continue, self.has_save_game),
            ("CONFIGURAÇÕES", self.on_settings, True),
            ("PERSONALIZAR JOGO", self.on_customize, True),
            ("TESTAR JUMPSCARES", self.on_test_jumpscare, True),
            ("SAIR", self.on_exit, True)
        ]
        self.selected_index: int = 0

        # Fontes
        self.title_font = pygame.font.SysFont("Georgia", 42, bold=True)
        self.subtitle_font = pygame.font.SysFont("Courier New", 14)
        self.btn_font = pygame.font.SysFont("Segoe UI", 16, bold=True)

    def set_has_save_game(self, has_save: bool):
        self.has_save_game = has_save
        self.options[1] = ("CONTINUAR", self.on_continue, self.has_save_game)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._change_selection(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._change_selection(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate_selected()

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            btn_w, btn_h = 320, 48
            start_y = 280
            for idx, (label, callback, enabled) in enumerate(self.options):
                bx = (self.screen_w - btn_w) // 2
                by = start_y + idx * (btn_h + 14)
                if pygame.Rect(bx, by, btn_w, btn_h).collidepoint(mx, my) and enabled:
                    if self.selected_index != idx:
                        self.selected_index = idx
                        self.audio_manager.play_ui_sound("click")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._activate_selected()

    def _change_selection(self, delta: int):
        prev = self.selected_index
        n = len(self.options)
        for _ in range(n):
            self.selected_index = (self.selected_index + delta) % n
            if self.options[self.selected_index][2]:  # se habilitado
                break
        if prev != self.selected_index:
            self.audio_manager.play_ui_sound("click")

    def _activate_selected(self):
        label, callback, enabled = self.options[self.selected_index]
        if enabled and callback:
            self.audio_manager.play_ui_sound("click")
            callback()

    def draw(self, surface: pygame.Surface):
        surface.fill((4, 6, 12))

        # Título atmosférico
        t = pygame.time.get_ticks() / 1000.0
        glow_alpha = int(math.sin(t * 1.5) * 30 + 220)

        title_surf = self.title_font.render("THE LAST CORRIDOR", True, (244, 63, 94))
        title_x = (self.screen_w - title_surf.get_width()) // 2
        surface.blit(title_surf, (title_x, 110))

        sub_surf = self.subtitle_font.render("JOGO DE TERROR PSICOLOGICO COM DESKTOP SIMULADO", True, (148, 163, 184))
        sub_x = (self.screen_w - sub_surf.get_width()) // 2
        surface.blit(sub_surf, (sub_x, 175))

        # Linha divisória fina
        pygame.draw.line(surface, (51, 65, 85), (self.screen_w // 2 - 200, 215), (self.screen_w // 2 + 200, 215), 1)

        # Botões de Menu
        btn_w, btn_h = 320, 48
        start_y = 270

        for idx, (label, callback, enabled) in enumerate(self.options):
            bx = (self.screen_w - btn_w) // 2
            by = start_y + idx * (btn_h + 14)
            rect = pygame.Rect(bx, by, btn_w, btn_h)

            is_sel = (idx == self.selected_index) and enabled

            # Fundo
            if not enabled:
                bg_col = (15, 23, 42)
                border_col = (30, 41, 59)
                txt_col = (71, 85, 105)
            elif is_sel:
                bg_col = (136, 19, 55)
                border_col = (244, 63, 94)
                txt_col = (255, 255, 255)
            else:
                bg_col = (22, 30, 49)
                border_col = (51, 65, 85)
                txt_col = (226, 232, 240)

            pygame.draw.rect(surface, bg_col, rect, border_radius=6)
            pygame.draw.rect(surface, border_col, rect, width=2 if is_sel else 1, border_radius=6)

            txt_surf = self.btn_font.render(label, True, txt_col)
            surface.blit(txt_surf, (bx + (btn_w - txt_surf.get_width()) // 2, by + (btn_h - txt_surf.get_height()) // 2))

            # Indicador de seleção
            if is_sel:
                pygame.draw.circle(surface, (244, 63, 94), (bx - 16, by + btn_h // 2), 4)
                pygame.draw.circle(surface, (244, 63, 94), (bx + btn_w + 16, by + btn_h // 2), 4)

        # Rodapé
        footer = self.subtitle_font.render("Use W/S ou Setas para navegar | ENTER para selecionar", True, (71, 85, 105))
        surface.blit(footer, ((self.screen_w - footer.get_width()) // 2, self.screen_h - 40))

"""
Janela da Mensagem Principal e Verificação do Código Secreto em THE LAST CORRIDOR.
Implementa a janela com o texto obrigatório:
'EXISTE UM ARQUIVO NO SEU COMPUTADOR, O ENCONTRE E ESCREVA O CODIGO AQUI'
"""

import pygame
import time
from typing import Tuple, Callable, Optional
try:
    from core.config import InvestigationConfig
    from core.audio_manager import AudioManager
except ImportError:
    from the_last_corridor.core.config import InvestigationConfig
    from the_last_corridor.core.audio_manager import AudioManager


class InvestigationWindow:
    def __init__(
        self,
        config: InvestigationConfig,
        audio_manager: AudioManager,
        on_success: Callable[[], None],
        x: int = 200,
        y: int = 80,
        w: int = 560,
        h: int = 280
    ):
        self.config = config
        self.audio_manager = audio_manager
        self.on_success = on_success

        self.rect = pygame.Rect(x, y, w, h)
        self.is_open: bool = True
        self.is_minimized: bool = False
        self.is_dragging: bool = False
        self.drag_offset: Tuple[int, int] = (0, 0)

        # Entrada de texto
        self.input_text: str = ""
        self.input_active: bool = True
        self.cursor_visible: bool = True
        self.last_cursor_toggle: float = time.time()
        self.feedback_msg: str = ""
        self.feedback_color: Tuple[int, int, int] = (180, 0, 0)
        self.feedback_time: float = 0.0

        # Estilo retrô (Janela cinza clássica com barra de título)
        self.bg_color = (192, 192, 192)
        self.title_bar_color = (0, 0, 128)
        self.border_light = (255, 255, 255)
        self.border_dark = (128, 128, 128)

        # Fontes
        self.title_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.prompt_font = pygame.font.SysFont("Courier New", 12, bold=True)
        self.input_font = pygame.font.SysFont("Courier New", 15, bold=True)
        self.btn_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.feedback_font = pygame.font.SysFont("Segoe UI", 11, bold=True)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.is_open or self.is_minimized:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Botão Minimizar [_]
            min_btn = pygame.Rect(self.rect.right - 36, self.rect.y + 4, 14, 14)
            if min_btn.collidepoint(mx, my):
                self.is_minimized = True
                self.audio_manager.play_ui_sound("click")
                return True

            # Barra de título (arraste)
            title_bar = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, 20)
            if title_bar.collidepoint(mx, my):
                self.is_dragging = True
                self.drag_offset = (mx - self.rect.x, my - self.rect.y)
                return True

            # Campo de entrada de texto
            input_rect = pygame.Rect(self.rect.x + 25, self.rect.y + 135, self.rect.w - 50, 34)
            self.input_active = input_rect.collidepoint(mx, my)

            # Botão "VERIFICAR CÓDIGO"
            btn_rect = pygame.Rect(self.rect.x + (self.rect.w - 180) // 2, self.rect.y + 185, 180, 36)
            if btn_rect.collidepoint(mx, my):
                self.audio_manager.play_ui_sound("click")
                self.verify_code()
                return True

            if self.rect.collidepoint(mx, my):
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mx, my = event.pos
                self.rect.x = mx - self.drag_offset[0]
                self.rect.y = my - self.drag_offset[1]
                return True

        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self.verify_code()
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            else:
                # Aceita letras, números e hífens
                char = event.unicode
                if len(self.input_text) < 32 and (char.isalnum() or char in ("-", "_", " ")):
                    self.input_text += char
                    return True

        return False

    def verify_code(self):
        user_input = self.input_text
        target_code = self.config.secret_code

        if self.config.strip_whitespace:
            user_input = user_input.strip()
            target_code = target_code.strip()

        if not self.config.case_sensitive:
            user_input = user_input.upper()
            target_code = target_code.upper()

        if user_input == target_code and user_input != "":
            self.feedback_msg = "CÓDIGO CORRETO! ACESSO AUTORIZADO."
            self.feedback_color = (0, 130, 0)
            self.feedback_time = time.time()
            self.audio_manager.play_ui_sound("success")
            self.on_success()
        else:
            self.feedback_msg = "CÓDIGO INCORRETO. ACESSO NEGADO."
            self.feedback_color = (180, 0, 0)
            self.feedback_time = time.time()
            self.audio_manager.play_ui_sound("error")

    def update(self):
        # Piscar do cursor
        if time.time() - self.last_cursor_toggle > 0.45:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = time.time()

    def draw(self, surface: pygame.Surface):
        if not self.is_open or self.is_minimized:
            return

        # Sombra
        pygame.draw.rect(surface, (0, 0, 0, 90), self.rect.move(4, 4))

        # Corpo
        pygame.draw.rect(surface, self.bg_color, self.rect)

        # Bordas 3D
        pygame.draw.line(surface, self.border_light, self.rect.topleft, self.rect.topright, 2)
        pygame.draw.line(surface, self.border_light, self.rect.topleft, self.rect.bottomleft, 2)
        pygame.draw.line(surface, self.border_dark, self.rect.bottomleft, self.rect.bottomright, 2)
        pygame.draw.line(surface, self.border_dark, self.rect.topright, self.rect.bottomright, 2)

        # Barra de título
        title_bar = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.w - 6, 18)
        pygame.draw.rect(surface, self.title_bar_color, title_bar)
        title_surf = self.title_font.render("TERMINAL RECOVERY SHELL - VERIFICACAO DE SEGURANCA", True, (255, 255, 255))
        surface.blit(title_surf, (self.rect.x + 8, self.rect.y + 4))

        # Botão Minimizar [_]
        min_btn = pygame.Rect(self.rect.right - 36, self.rect.y + 4, 14, 14)
        pygame.draw.rect(surface, (192, 192, 192), min_btn)
        pygame.draw.rect(surface, (0, 0, 0), min_btn, 1)
        pygame.draw.line(surface, (0, 0, 0), (min_btn.x + 3, min_btn.bottom - 4), (min_btn.right - 4, min_btn.bottom - 4), 2)

        # A MENSAGEM PRINCIPAL OBRIGATÓRIA (EXATAMENTE COMO ESCRITA)
        # "EXISTE UM ARQUIVO NO SEU COMPUTADOR, O ENCONTRE E ESCREVA O CODIGO AQUI"
        msg_box = pygame.Rect(self.rect.x + 16, self.rect.y + 30, self.rect.w - 32, 90)
        pygame.draw.rect(surface, (10, 15, 25), msg_box)
        pygame.draw.rect(surface, (0, 0, 0), msg_box, 1)

        # Renderiza a mensagem em linhas bem visíveis
        line1 = "EXISTE UM ARQUIVO NO SEU COMPUTADOR,"
        line2 = "O ENCONTRE E ESCREVA O CODIGO AQUI"
        surf_l1 = self.prompt_font.render(line1, True, (254, 240, 138))
        surf_l2 = self.prompt_font.render(line2, True, (254, 240, 138))
        surface.blit(surf_l1, (msg_box.x + (msg_box.w - surf_l1.get_width()) // 2, msg_box.y + 20))
        surface.blit(surf_l2, (msg_box.x + (msg_box.w - surf_l2.get_width()) // 2, msg_box.y + 45))

        # Campo de Entrada de Código
        input_rect = pygame.Rect(self.rect.x + 25, self.rect.y + 135, self.rect.w - 50, 34)
        pygame.draw.rect(surface, (255, 255, 255), input_rect)
        border_col = (0, 0, 128) if self.input_active else self.border_dark
        pygame.draw.rect(surface, border_col, input_rect, 2)

        # Texto do código digitado
        display_str = self.input_text + ("|" if (self.input_active and self.cursor_visible) else "")
        code_surf = self.input_font.render(display_str, True, (15, 23, 42))
        surface.blit(code_surf, (input_rect.x + 10, input_rect.y + 7))

        # Botão "VERIFICAR CÓDIGO"
        btn_rect = pygame.Rect(self.rect.x + (self.rect.w - 180) // 2, self.rect.y + 185, 180, 36)
        pygame.draw.rect(surface, (210, 210, 210), btn_rect)
        pygame.draw.line(surface, self.border_light, btn_rect.topleft, btn_rect.topright, 2)
        pygame.draw.line(surface, self.border_light, btn_rect.topleft, btn_rect.bottomleft, 2)
        pygame.draw.line(surface, self.border_dark, btn_rect.bottomleft, btn_rect.bottomright, 2)
        pygame.draw.line(surface, self.border_dark, btn_rect.topright, btn_rect.bottomright, 2)

        btn_txt = self.btn_font.render("VERIFICAR CÓDIGO", True, (0, 0, 0))
        surface.blit(btn_txt, (btn_rect.x + (btn_rect.w - btn_txt.get_width()) // 2, btn_rect.y + 9))

        # Mensagem de Feedback
        if self.feedback_msg and (time.time() - self.feedback_time < 4.0):
            fb_surf = self.feedback_font.render(self.feedback_msg, True, self.feedback_color)
            surface.blit(fb_surf, (self.rect.x + (self.rect.w - fb_surf.get_width()) // 2, self.rect.y + 235))

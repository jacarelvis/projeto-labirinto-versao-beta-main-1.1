"""
Visualizador de Documentos de Texto (Bloco de Notas Retrô) do Computador Simulado.
Apresenta pistas narrativas e o documento final com estética do Windows 95/98.
"""

import pygame
from typing import List, Optional, Tuple


class TextDocumentWindow:
    def __init__(self, filename: str, content: str, x: int = 240, y: int = 120, w: int = 480, h: int = 360):
        self.filename = filename
        self.content = content
        self.rect = pygame.Rect(x, y, w, h)
        self.is_open: bool = True
        self.is_dragging: bool = False
        self.drag_offset: Tuple[int, int] = (0, 0)

        # Cores retrô clássicas do Windows 95
        self.bg_color = (192, 192, 192)
        self.title_bar_active = (0, 0, 128)  # Azul clássico
        self.title_text_color = (255, 255, 255)
        self.border_light = (255, 255, 255)
        self.border_dark = (128, 128, 128)
        self.text_area_bg = (255, 255, 255)
        self.text_color = (10, 10, 10)

        # Fontes
        self.title_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.doc_font = pygame.font.SysFont("Courier New", 12)

        self.lines: List[str] = self._prepare_lines()

    def _prepare_lines(self) -> List[str]:
        raw_lines = self.content.split("\n")
        formatted = []
        for rl in raw_lines:
            # Quebra linhas longas em 55 caracteres
            while len(rl) > 55:
                formatted.append(rl[:55])
                rl = rl[55:]
            formatted.append(rl)
        return formatted

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Processa cliques e arrasto de janela. Retorna True se consumiu o evento."""
        if not self.is_open:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Verificar botão de fechar [X]
            close_btn = pygame.Rect(self.rect.right - 20, self.rect.y + 3, 16, 14)
            if close_btn.collidepoint(mx, my):
                self.is_open = False
                return True

            # Barra de título para arrastar
            title_bar = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, 20)
            if title_bar.collidepoint(mx, my):
                self.is_dragging = True
                self.drag_offset = (mx - self.rect.x, my - self.rect.y)
                return True

            # Clique dentro da janela
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

        return False

    def draw(self, surface: pygame.Surface):
        if not self.is_open:
            return

        # Sombra da janela
        pygame.draw.rect(surface, (0, 0, 0, 80), self.rect.move(4, 4))

        # Corpo da janela (Cinza Win95)
        pygame.draw.rect(surface, self.bg_color, self.rect)

        # Bordas chanfradas 3D
        pygame.draw.line(surface, self.border_light, self.rect.topleft, self.rect.topright, 2)
        pygame.draw.line(surface, self.border_light, self.rect.topleft, self.rect.bottomleft, 2)
        pygame.draw.line(surface, self.border_dark, self.rect.bottomleft, self.rect.bottomright, 2)
        pygame.draw.line(surface, self.border_dark, self.rect.topright, self.rect.bottomright, 2)

        # Barra de título azul
        title_bar = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.w - 6, 18)
        pygame.draw.rect(surface, self.title_bar_active, title_bar)

        # Texto do título
        title_txt = self.title_font.render(f"Bloco de Notas - {self.filename}", True, self.title_text_color)
        surface.blit(title_txt, (self.rect.x + 8, self.rect.y + 4))

        # Botão Fechar [X]
        close_btn = pygame.Rect(self.rect.right - 20, self.rect.y + 5, 14, 14)
        pygame.draw.rect(surface, (192, 192, 192), close_btn)
        pygame.draw.rect(surface, (0, 0, 0), close_btn, 1)
        x_txt = self.title_font.render("X", True, (0, 0, 0))
        surface.blit(x_txt, (close_btn.x + 3, close_btn.y))

        # Área de texto interna branca
        text_rect = pygame.Rect(self.rect.x + 8, self.rect.y + 26, self.rect.w - 16, self.rect.h - 34)
        pygame.draw.rect(surface, self.text_area_bg, text_rect)
        pygame.draw.rect(surface, self.border_dark, text_rect, 1)

        # Renderizar linhas de texto
        line_y = text_rect.y + 6
        for line in self.lines:
            if line_y + 14 > text_rect.bottom - 4:
                break
            txt_surf = self.doc_font.render(line, True, self.text_color)
            surface.blit(txt_surf, (text_rect.x + 8, line_y))
            line_y += 16

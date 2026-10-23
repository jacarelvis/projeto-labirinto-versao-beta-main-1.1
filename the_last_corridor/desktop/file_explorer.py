"""
Explorador de Arquivos do Computador Simulado em THE LAST CORRIDOR.
Permite navegar por pastas, subpastas e abrir documentos com interface retrô dos anos 90.
"""

import pygame
import time
from typing import List, Tuple, Optional, Callable, Dict, Any
from .virtual_filesystem import VirtualFileSystem, VirtualNode
try:
    from core.asset_manager import AssetManager
    from core.audio_manager import AudioManager
except ImportError:
    from the_last_corridor.core.asset_manager import AssetManager
    from the_last_corridor.core.audio_manager import AudioManager


class FileExplorerWindow:
    def __init__(
        self,
        vfs: VirtualFileSystem,
        asset_manager: AssetManager,
        audio_manager: AudioManager,
        on_open_folder: Callable[[str], None],
        on_open_file: Callable[[str, str, str], None],
        dangerous_paths: Dict[str, Any],
        x: int = 80,
        y: int = 140,
        w: int = 600,
        h: int = 420
    ):
        self.vfs = vfs
        self.asset_manager = asset_manager
        self.audio_manager = audio_manager
        self.on_open_folder = on_open_folder
        self.on_open_file = on_open_file
        self.dangerous_paths = dangerous_paths

        self.current_path: str = "root"
        self.rect = pygame.Rect(x, y, w, h)
        self.is_open: bool = True
        self.is_dragging: bool = False
        self.drag_offset: Tuple[int, int] = (0, 0)

        # Seleção e clique duplo
        self.selected_item: Optional[str] = None
        self.last_click_time: float = 0.0
        self.last_clicked_item: Optional[str] = None

        # Estilo retrô
        self.bg_color = (192, 192, 192)
        self.title_bar_color = (0, 0, 128)
        self.border_light = (255, 255, 255)
        self.border_dark = (128, 128, 128)
        self.client_area_bg = (255, 255, 255)

        # Fontes
        self.title_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.path_font = pygame.font.SysFont("Courier New", 11)
        self.item_font = pygame.font.SysFont("Segoe UI", 11)

    def navigate_to(self, path: str):
        """Muda para o diretório indicado."""
        self.current_path = path
        self.selected_item = None

    def go_back(self):
        """Retorna para a pasta mãe."""
        if self.current_path == "root" or not self.current_path:
            return
        parts = self.current_path.split("/")
        if len(parts) > 1:
            self.navigate_to("/".join(parts[:-1]))
        else:
            self.navigate_to("root")

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.is_open:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Fechar [X]
            close_btn = pygame.Rect(self.rect.right - 20, self.rect.y + 3, 16, 14)
            if close_btn.collidepoint(mx, my):
                self.is_open = False
                self.audio_manager.play_ui_sound("click")
                return True

            # Barra de título
            title_bar = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, 20)
            if title_bar.collidepoint(mx, my):
                self.is_dragging = True
                self.drag_offset = (mx - self.rect.x, my - self.rect.y)
                return True

            # Botão "Voltar" [ < Voltar ]
            back_btn = pygame.Rect(self.rect.x + 8, self.rect.y + 26, 75, 22)
            if back_btn.collidepoint(mx, my):
                self.audio_manager.play_ui_sound("click")
                self.go_back()
                return True

            # Itens dentro da área de arquivos
            content_rect = pygame.Rect(self.rect.x + 8, self.rect.y + 54, self.rect.w - 16, self.rect.h - 62)
            if content_rect.collidepoint(mx, my):
                self._handle_item_click(mx, my)
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

        return False

    def _handle_item_click(self, mx: int, my: int):
        now = time.time()
        is_double_click = (now - self.last_click_time < 0.4)

        items = self.vfs.list_children(self.current_path)
        item_w, item_h = 90, 75
        cols = max(1, (self.rect.w - 30) // item_w)

        clicked_name = None
        clicked_type = None

        start_x = self.rect.x + 16
        start_y = self.rect.y + 64

        for idx, (name, node_type) in enumerate(items):
            col = idx % cols
            row = idx // cols
            ix = start_x + col * item_w
            iy = start_y + row * item_h
            item_rect = pygame.Rect(ix, iy, item_w, item_h)

            if item_rect.collidepoint(mx, my):
                clicked_name = name
                clicked_type = node_type
                break

        if clicked_name:
            self.selected_item = clicked_name

            if is_double_click and self.last_clicked_item == clicked_name:
                # Dispara abertura de item
                target_path = f"{self.current_path}/{clicked_name}" if self.current_path != "root" else clicked_name
                if clicked_type == "folder":
                    self.on_open_folder(target_path)
                else:
                    content = self.vfs.get_file_content(target_path) or ""
                    self.on_open_file(target_path, clicked_name, content)

            self.last_click_time = now
            self.last_clicked_item = clicked_name
        else:
            self.selected_item = None

    def draw(self, surface: pygame.Surface):
        if not self.is_open:
            return

        # Sombra
        pygame.draw.rect(surface, (0, 0, 0, 80), self.rect.move(4, 4))

        # Corpo
        pygame.draw.rect(surface, self.bg_color, self.rect)

        # Bordas 3D
        pygame.draw.line(surface, self.border_light, self.rect.topleft, self.rect.topright, 2)
        pygame.draw.line(surface, self.border_light, self.rect.topleft, self.rect.bottomleft, 2)
        pygame.draw.line(surface, self.border_dark, self.rect.bottomleft, self.rect.bottomright, 2)
        pygame.draw.line(surface, self.border_dark, self.rect.topright, self.rect.bottomright, 2)

        # Barra de título azul
        title_bar = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.w - 6, 18)
        pygame.draw.rect(surface, self.title_bar_color, title_bar)
        disp_title = f"Explorador de Arquivos - C:\\{self.current_path.replace('/', '\\')}"
        title_txt = self.title_font.render(disp_title, True, (255, 255, 255))
        surface.blit(title_txt, (self.rect.x + 8, self.rect.y + 4))

        # Botão Fechar [X]
        close_btn = pygame.Rect(self.rect.right - 20, self.rect.y + 4, 16, 14)
        pygame.draw.rect(surface, (192, 192, 192), close_btn)
        pygame.draw.rect(surface, (0, 0, 0), close_btn, 1)
        x_txt = self.title_font.render("X", True, (0, 0, 0))
        surface.blit(x_txt, (close_btn.x + 4, close_btn.y))

        # Botão Voltar [ < Voltar ]
        back_btn = pygame.Rect(self.rect.x + 8, self.rect.y + 26, 75, 22)
        pygame.draw.rect(surface, (210, 210, 210), back_btn)
        pygame.draw.line(surface, self.border_light, back_btn.topleft, back_btn.topright, 2)
        pygame.draw.line(surface, self.border_light, back_btn.topleft, back_btn.bottomleft, 2)
        pygame.draw.line(surface, self.border_dark, back_btn.bottomleft, back_btn.bottomright, 2)
        pygame.draw.line(surface, self.border_dark, back_btn.topright, back_btn.bottomright, 2)
        back_txt = self.title_font.render("◀ Voltar", True, (0, 0, 0))
        surface.blit(back_txt, (back_btn.x + 8, back_btn.y + 3))

        # Barra de Endereço
        addr_rect = pygame.Rect(self.rect.x + 90, self.rect.y + 26, self.rect.w - 98, 22)
        pygame.draw.rect(surface, (255, 255, 255), addr_rect)
        pygame.draw.rect(surface, self.border_dark, addr_rect, 1)
        path_txt = self.path_font.render(f"C:\\{self.current_path.replace('/', '\\')}", True, (20, 20, 20))
        surface.blit(path_txt, (addr_rect.x + 6, addr_rect.y + 3))

        # Área de Conteúdo
        content_rect = pygame.Rect(self.rect.x + 8, self.rect.y + 54, self.rect.w - 16, self.rect.h - 62)
        pygame.draw.rect(surface, self.client_area_bg, content_rect)
        pygame.draw.rect(surface, self.border_dark, content_rect, 1)

        # Listagem de Pastas e Arquivos
        items = self.vfs.list_children(self.current_path)
        item_w, item_h = 90, 75
        cols = max(1, (self.rect.w - 30) // item_w)
        start_x = self.rect.x + 16
        start_y = self.rect.y + 64

        folder_icon = self.asset_manager.load_image("", (36, 36), fallback_type="folder")
        danger_folder_icon = self.asset_manager.load_image("", (36, 36), fallback_type="danger_folder")
        file_icon = self.asset_manager.load_image("", (32, 36), fallback_type="file")

        for idx, (name, node_type) in enumerate(items):
            col = idx % cols
            row = idx // cols
            ix = start_x + col * item_w
            iy = start_y + row * item_h

            if iy + item_h > content_rect.bottom:
                break

            full_item_path = f"{self.current_path}/{name}" if self.current_path != "root" else name
            is_danger = full_item_path in self.dangerous_paths and self.dangerous_paths[full_item_path].status == "dangerous"

            # Fundo de seleção
            if self.selected_item == name:
                sel_rect = pygame.Rect(ix, iy, item_w - 4, item_h - 4)
                pygame.draw.rect(surface, (0, 0, 128), sel_rect)

            # Ícone
            if node_type == "folder":
                icon_surf = danger_folder_icon if is_danger else folder_icon
            else:
                icon_surf = file_icon

            icon_x = ix + (item_w - icon_surf.get_width()) // 2
            surface.blit(icon_surf, (icon_x, iy + 6))

            # Nome do item
            label_col = (255, 255, 255) if self.selected_item == name else (0, 0, 0)
            short_name = name if len(name) <= 12 else name[:10] + ".."
            lbl_surf = self.item_font.render(short_name, True, label_col)
            lbl_x = ix + (item_w - lbl_surf.get_width()) // 2
            surface.blit(lbl_surf, (lbl_x, iy + 46))

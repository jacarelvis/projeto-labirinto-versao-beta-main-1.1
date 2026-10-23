"""
Computador Antigo Simulado de THE LAST CORRIDOR.
Gerencia a sequência de inicialização, desktop retrô com barra de tarefas,
pastas perigosas com jumpscares específicos, exploração de arquivos e vitória.
"""

import pygame
import time
from typing import List, Optional, Tuple, Callable
from .virtual_filesystem import VirtualFileSystem
from .file_explorer import FileExplorerWindow
from .virtual_documents import TextDocumentWindow
from .investigation import InvestigationWindow
try:
    from core.config import DesktopConfig, InvestigationConfig, DangerousFolderConfig
    from core.asset_manager import AssetManager
    from core.audio_manager import AudioManager
except ImportError:
    from the_last_corridor.core.config import DesktopConfig, InvestigationConfig, DangerousFolderConfig
    from the_last_corridor.core.asset_manager import AssetManager
    from the_last_corridor.core.audio_manager import AudioManager


class VirtualComputer:
    def __init__(
        self,
        desktop_cfg: DesktopConfig,
        investigation_cfg: InvestigationConfig,
        dangerous_folders: dict,
        filesystem_tree: dict,
        asset_manager: AssetManager,
        audio_manager: AudioManager,
        on_victory: Callable[[], None],
        screen_w: int = 1024,
        screen_h: int = 768
    ):
        self.desktop_cfg = desktop_cfg
        self.investigation_cfg = investigation_cfg
        self.dangerous_folders = dangerous_folders
        self.asset_manager = asset_manager
        self.audio_manager = audio_manager
        self.on_victory = on_victory
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Sistema de Arquivos Virtual
        self.vfs = VirtualFileSystem(filesystem_tree)

        # Estado de Boot
        self.is_booting: bool = True
        self.boot_start_time: float = 0.0
        self.boot_lines_shown: int = 0
        self.boot_beep_played: bool = False
        self.boot_degauss_played: bool = False
        self.boot_seek_played: bool = False

        # Estado do Desktop
        self.explorer = FileExplorerWindow(
            vfs=self.vfs,
            asset_manager=self.asset_manager,
            audio_manager=self.audio_manager,
            on_open_folder=self.handle_folder_open,
            on_open_file=self.handle_file_open,
            dangerous_paths=self.dangerous_folders,
            x=60,
            y=120,
            w=580,
            h=420
        )
        self.investigation_win = InvestigationWindow(
            config=self.investigation_cfg,
            audio_manager=self.audio_manager,
            on_success=self.handle_code_success,
            x=220,
            y=60,
            w=580,
            h=280
        )
        self.doc_windows: List[TextDocumentWindow] = []

        # Jumpscare de Pasta Perigosa Ativo
        self.active_folder_scare: Optional[DangerousFolderConfig] = None
        self.folder_scare_start: float = 0.0

        # Fontes do Desktop
        self.boot_font = pygame.font.SysFont("Courier New", 14, bold=True)
        self.desktop_icon_font = pygame.font.SysFont("Segoe UI", 11)
        self.taskbar_font = pygame.font.SysFont("Segoe UI", 11, bold=True)

    def start_boot(self):
        """Inicia a sequência de boot simulada."""
        self.is_booting = True
        self.boot_start_time = time.time()
        self.boot_lines_shown = 0
        self.boot_beep_played = False
        self.boot_degauss_played = False
        self.boot_seek_played = False
        self.active_folder_scare = None
        self.doc_windows.clear()

        # Inicia a mensagem de investigação aberta e no topo
        self.investigation_win.is_open = True
        self.investigation_win.is_minimized = False
        self.explorer.is_open = True
        self.explorer.navigate_to("Desktop")

    def update(self, dt: float) -> Optional[str]:
        """Atualiza boot, sustos e janelas. Retorna 'victory' se completado."""
        now = time.time()

        # 1. Sequência de Inicialização (Boot)
        if self.is_booting:
            elapsed = (now - self.boot_start_time) * 1000.0
            total_lines = len(self.desktop_cfg.boot_lines)

            # Efeitos de áudio da inicialização retrô
            if not self.boot_degauss_played and elapsed > 80:
                self.audio_manager.play_computer_sound("crt_degauss")
                self.boot_degauss_played = True

            if not self.boot_beep_played and elapsed > 450:
                self.audio_manager.play_computer_sound("pc_boot_beep")
                self.boot_beep_played = True

            if not self.boot_seek_played and elapsed > 1300:
                self.audio_manager.play_computer_sound("drive_seek")
                self.boot_seek_played = True

            # Revelar linhas conforme o tempo passa
            line_interval = max(200.0, self.desktop_cfg.boot_duration_ms / (total_lines + 1))
            self.boot_lines_shown = min(total_lines, int(elapsed / line_interval))

            if elapsed >= self.desktop_cfg.boot_duration_ms:
                self.is_booting = False
                # Inicia ambiente sonoro do desktop (zumbido elétrico e CRT)
                self.audio_manager.start_ambient_drone("desktop")
            return None

        # 2. Jumpscare de Pasta Perigosa Ativo
        if self.active_folder_scare is not None:
            scare_elapsed = (now - self.folder_scare_start) * 1000.0
            if scare_elapsed >= self.active_folder_scare.duration_ms:
                # Fim do susto
                if self.active_folder_scare.return_to_parent:
                    self.explorer.go_back()
                self.active_folder_scare = None
                self.audio_manager.resume_ambient()
            return None

        # 3. Atualizar janela de investigação
        self.investigation_win.update()
        return None

    def handle_folder_open(self, path: str):
        """Avalia se a pasta aberta é perigosa, suspeita ou segura."""
        clean_path = path.strip("/")
        danger_cfg = self.dangerous_folders.get(clean_path)

        if danger_cfg and danger_cfg.status == "dangerous":
            if not (danger_cfg.trigger_once and danger_cfg.has_triggered):
                # Dispara JUMPSCARE DA PASTA PERIGOSA com som específico
                danger_cfg.has_triggered = True
                self.active_folder_scare = danger_cfg
                self.folder_scare_start = time.time()
                sound_type = getattr(danger_cfg, "sound_type", "scream")
                self.audio_manager.play_jumpscare(
                    path_str=danger_cfg.scare_audio,
                    sound_type=sound_type,
                    volume_mult=danger_cfg.volume
                )
                return

        elif danger_cfg and danger_cfg.status == "suspicious":
            self.audio_manager.play_ui_sound("error")

        # Pasta normal
        self.audio_manager.play_ui_sound("folder_open")
        self.explorer.navigate_to(clean_path)

    def handle_file_open(self, path: str, filename: str, content: str):
        """Abre uma nova janela de leitura de documento de texto."""
        self.audio_manager.play_ui_sound("doc_open")
        # Cria janela de documento com leve deslocamento para cada novo arquivo
        offset = (len(self.doc_windows) % 5) * 25
        doc_win = TextDocumentWindow(
            filename=filename,
            content=content,
            x=180 + offset,
            y=140 + offset,
            w=500,
            h=360
        )
        self.doc_windows.append(doc_win)

    def handle_code_success(self):
        """Chamado quando o jogador acerta o código secreto."""
        self.on_victory()

    def handle_event(self, event: pygame.event.Event):
        if self.is_booting or self.active_folder_scare is not None:
            return

        # 1. Eventos da Janela de Investigação (prioridade se aberta)
        if self.investigation_win.is_open and not self.investigation_win.is_minimized:
            if self.investigation_win.handle_event(event):
                return

        # 2. Eventos das Janelas de Documentos Abertas (do topo para base)
        for doc_win in reversed(self.doc_windows):
            if doc_win.is_open:
                if doc_win.handle_event(event):
                    return

        # Limpar janelas fechadas
        self.doc_windows = [dw for dw in self.doc_windows if dw.is_open]

        # 3. Eventos do Explorador de Arquivos
        if self.explorer.is_open:
            if self.explorer.handle_event(event):
                return

        # 4. Ícones do Desktop e Barra de Tarefas
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Ícone "Meu Computador"
            my_pc_rect = pygame.Rect(20, 20, 70, 70)
            if my_pc_rect.collidepoint(mx, my):
                self.explorer.is_open = True
                self.explorer.navigate_to("root")
                self.audio_manager.play_ui_sound("click")
                return

            # Ícone "Mensagem do Sistema"
            msg_icon_rect = pygame.Rect(20, 100, 70, 70)
            if msg_icon_rect.collidepoint(mx, my):
                self.investigation_win.is_open = True
                self.investigation_win.is_minimized = False
                self.audio_manager.play_ui_sound("click")
                return

            # Barra de tarefas: Botão da Janela de Investigação
            tb_inv_rect = pygame.Rect(110, self.screen_h - 26, 170, 22)
            if tb_inv_rect.collidepoint(mx, my):
                self.investigation_win.is_open = True
                self.investigation_win.is_minimized = not self.investigation_win.is_minimized
                self.audio_manager.play_ui_sound("click")
                return

            # Barra de tarefas: Botão do Explorador
            tb_exp_rect = pygame.Rect(285, self.screen_h - 26, 150, 22)
            if tb_exp_rect.collidepoint(mx, my):
                self.explorer.is_open = not self.explorer.is_open
                self.audio_manager.play_ui_sound("click")
                return

    def draw(self, surface: pygame.Surface, reduce_flashes: bool = False, reduce_shakes: bool = False):
        # 1. Tela de Boot
        if self.is_booting:
            surface.fill((0, 0, 0))
            y = 40
            for i in range(self.boot_lines_shown):
                line = self.desktop_cfg.boot_lines[i]
                line_col = (255, 255, 255) if "WARNING" not in line and "ERROR" not in line else (239, 68, 68)
                line_surf = self.boot_font.render(line, True, line_col)
                surface.blit(line_surf, (40, y))
                y += 26
            return

        # 2. Jumpscare de Pasta Perigosa
        if self.active_folder_scare is not None:
            surface.fill((0, 0, 0))
            cfg = self.active_folder_scare
            now = time.time()
            elapsed = (now - self.folder_scare_start) * 1000.0

            # Tremor violento
            shake_x, shake_y = 0, 0
            if cfg.shake and not reduce_shakes:
                import random
                shake_x = random.randint(-24, 24)
                shake_y = random.randint(-24, 24)

            # Imagem do susto da pasta
            scare_img = self.asset_manager.load_image(
                cfg.scare_image,
                target_size=(self.screen_w, self.screen_h),
                fallback_type="jumpscare"
            )
            surface.blit(scare_img, (shake_x, shake_y))

            # Flash estroboscópico inicial
            if elapsed < 120 and not reduce_flashes:
                flash_surf = pygame.Surface((self.screen_w, self.screen_h))
                flash_surf.fill((255, 255, 255))
                surface.blit(flash_surf, (0, 0))
            return

        # 3. Fundo do Desktop (Wallpaper retrô teal)
        wallpaper = self.asset_manager.load_image(
            self.desktop_cfg.wallpaper_image,
            target_size=(self.screen_w, self.screen_h - 28),
            fallback_type="wallpaper"
        )
        surface.blit(wallpaper, (0, 0))

        # 4. Ícones do Desktop
        # Ícone "Meu Computador"
        folder_icon = self.asset_manager.load_image("", (40, 40), fallback_type="folder")
        surface.blit(folder_icon, (35, 25))
        lbl_pc = self.desktop_icon_font.render("Meu Computador", True, (255, 255, 255))
        surface.blit(lbl_pc, (20, 70))

        # Ícone "Mensagem do Sistema"
        file_icon = self.asset_manager.load_image("", (36, 40), fallback_type="file")
        surface.blit(file_icon, (37, 105))
        lbl_msg = self.desktop_icon_font.render("Mensagem", True, (255, 255, 255))
        surface.blit(lbl_msg, (32, 150))

        # 5. Janelas Abertas
        if self.explorer.is_open:
            self.explorer.draw(surface)

        for doc_win in self.doc_windows:
            if doc_win.is_open:
                doc_win.draw(surface)

        if self.investigation_win.is_open:
            self.investigation_win.draw(surface)

        # 6. Barra de Tarefas (Taskbar retrô clássica na base)
        tb_y = self.screen_h - 28
        tb_rect = pygame.Rect(0, tb_y, self.screen_w, 28)
        pygame.draw.rect(surface, (192, 192, 192), tb_rect)
        pygame.draw.line(surface, (255, 255, 255), (0, tb_y), (self.screen_w, tb_y), 2)

        # Botão Iniciar [ Iniciar ]
        start_btn = pygame.Rect(4, tb_y + 3, 72, 22)
        pygame.draw.rect(surface, (210, 210, 210), start_btn)
        pygame.draw.line(surface, (255, 255, 255), start_btn.topleft, start_btn.topright, 2)
        pygame.draw.line(surface, (255, 255, 255), start_btn.topleft, start_btn.bottomleft, 2)
        pygame.draw.line(surface, (128, 128, 128), start_btn.bottomleft, start_btn.bottomright, 2)
        pygame.draw.line(surface, (128, 128, 128), start_btn.topright, start_btn.bottomright, 2)

        start_lbl = self.taskbar_font.render(self.desktop_cfg.computer_name, True, (0, 0, 0))
        surface.blit(start_lbl, (start_btn.x + 6, start_btn.y + 4))

        # Botões de janelas na barra
        tb_inv_rect = pygame.Rect(82, tb_y + 3, 160, 22)
        pygame.draw.rect(surface, (210, 210, 210) if not self.investigation_win.is_minimized else (180, 180, 180), tb_inv_rect)
        pygame.draw.rect(surface, (128, 128, 128), tb_inv_rect, 1)
        inv_lbl = self.taskbar_font.render("Verificacao de Codigo", True, (0, 0, 0))
        surface.blit(inv_lbl, (tb_inv_rect.x + 6, tb_inv_rect.y + 4))

        if self.explorer.is_open:
            tb_exp_rect = pygame.Rect(248, tb_y + 3, 140, 22)
            pygame.draw.rect(surface, (210, 210, 210), tb_exp_rect)
            pygame.draw.rect(surface, (128, 128, 128), tb_exp_rect, 1)
            exp_lbl = self.taskbar_font.render("Explorador", True, (0, 0, 0))
            surface.blit(exp_lbl, (tb_exp_rect.x + 8, tb_exp_rect.y + 4))

        # Relógio Fictício Sombrio ("03:33")
        clock_rect = pygame.Rect(self.screen_w - 75, tb_y + 3, 70, 22)
        pygame.draw.rect(surface, (192, 192, 192), clock_rect)
        pygame.draw.rect(surface, (128, 128, 128), clock_rect, 1)
        clock_lbl = self.taskbar_font.render("03:33", True, (0, 0, 0))
        surface.blit(clock_lbl, (clock_rect.x + 18, clock_rect.y + 4))

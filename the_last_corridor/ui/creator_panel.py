"""
Painel de Personalização do Criador em THE LAST CORRIDOR.
Permite configurar labirinto, aparições, jumpscares, sistema completo de áudio de terror,
pastas perigosas, código secreto e salvar/carregar perfis JSON diretamente pela interface gráfica.
"""

import pygame
from typing import Callable, List, Optional
from pathlib import Path

try:
    from core.config import GameConfig, ApparitionItem, DangerousFolderConfig
    from core.save_manager import SaveManager
    from core.audio_manager import AudioManager
except ImportError:
    from the_last_corridor.core.config import GameConfig, ApparitionItem, DangerousFolderConfig
    from the_last_corridor.core.save_manager import SaveManager
    from the_last_corridor.core.audio_manager import AudioManager


class CreatorPanel:
    def __init__(
        self,
        config: GameConfig,
        save_manager: SaveManager,
        audio_manager: AudioManager,
        on_back: Callable[[], None],
        screen_w: int = 1024,
        screen_h: int = 768
    ):
        self.config = config
        self.save_manager = save_manager
        self.audio_manager = audio_manager
        self.on_back = on_back
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Abas do Painel
        self.tabs = [
            "LABIRINTO",
            "APARIÇÕES",
            "JUMPSCARE",
            "ÁUDIO & BIBLIOTECA",
            "DESKTOP & PASTAS",
            "CÓDIGO & FINAL",
            "PERFIS"
        ]
        self.current_tab_idx: int = 0

        # Seleção de áudio para teste e associação
        self.preview_sounds = [
            ("Grito Distorcido", "scream"),
            ("Rugido Monstruoso", "roar"),
            ("Impacto Metálico", "impact_screech"),
            ("Distorção Extrema", "distortion"),
            ("Glitch Digital", "glitch"),
            ("Estática TV", "static"),
            ("Sussurro Espectral", "whisper"),
            ("Monitor CRT Degauss", "crt_degauss"),
            ("Disco Rígido IDE", "drive_seek")
        ]
        self.selected_preview_idx = 0

        # Entrada de texto ativa
        self.active_input_field: Optional[str] = None
        self.temp_inputs = {
            "secret_code": self.config.investigation.secret_code,
            "computer_name": self.config.desktop.computer_name,
            "danger_folder": "Meus Documentos/Pessoal/nao_abra",
            "profile_name": "meu_perfil_terror",
            "import_audio": "meu_som.wav"
        }
        self.status_message: str = ""

        # Fontes
        self.title_font = pygame.font.SysFont("Georgia", 24, bold=True)
        self.tab_font = pygame.font.SysFont("Segoe UI", 11, bold=True)
        self.label_font = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.val_font = pygame.font.SysFont("Segoe UI", 12)
        self.input_font = pygame.font.SysFont("Courier New", 13, bold=True)
        self.small_font = pygame.font.SysFont("Segoe UI", 10)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.audio_manager.stop_preview()
                self.audio_manager.play_ui_sound("click")
                self.on_back()
                return

            # Digitação em campo ativo
            if self.active_input_field:
                if event.key == pygame.K_RETURN:
                    self._apply_text_input(self.active_input_field)
                    self.active_input_field = None
                elif event.key == pygame.K_BACKSPACE:
                    self.temp_inputs[self.active_input_field] = self.temp_inputs[self.active_input_field][:-1]
                else:
                    char = event.unicode
                    if len(self.temp_inputs[self.active_input_field]) < 45 and (char.isalnum() or char in ("-", "_", "/", " ", ".", ":", "\\")):
                        self.temp_inputs[self.active_input_field] += char

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Clique nas Abas
            tab_w = (self.screen_w - 60) // len(self.tabs)
            for idx, tab_name in enumerate(self.tabs):
                tab_rect = pygame.Rect(30 + idx * tab_w, 75, tab_w - 4, 38)
                if tab_rect.collidepoint(mx, my):
                    self.current_tab_idx = idx
                    self.active_input_field = None
                    self.audio_manager.stop_preview()
                    self.audio_manager.play_ui_sound("click")
                    return

            # Botão Voltar ao Menu
            back_btn = pygame.Rect(self.screen_w - 140, 20, 110, 36)
            if back_btn.collidepoint(mx, my):
                self.audio_manager.stop_preview()
                self.audio_manager.play_ui_sound("click")
                self.on_back()
                return

            # Clique dentro da aba ativa
            self._handle_tab_click(mx, my)

    def _apply_text_input(self, field_name: str):
        val = self.temp_inputs[field_name].strip()
        if field_name == "secret_code" and val:
            self.config.investigation.secret_code = val
            self.status_message = f"Código secreto alterado para '{val}'."
        elif field_name == "computer_name" and val:
            self.config.desktop.computer_name = val
            self.status_message = f"Nome do computador alterado para '{val}'."
        elif field_name == "import_audio" and val:
            ok, msg = self.audio_manager.import_audio_file(val, category="jumpscares")
            if ok:
                self.status_message = f"Áudio importado com sucesso: {msg}"
            else:
                self.status_message = f"Falha na importação: {msg}"

    def _handle_tab_click(self, mx: int, my: int):
        tab = self.tabs[self.current_tab_idx]

        if tab == "LABIRINTO":
            for idx, size in enumerate([15, 19, 25]):
                if pygame.Rect(260 + idx * 110, 170, 95, 34).collidepoint(mx, my):
                    self.config.maze.cols = size
                    self.config.maze.rows = size
                    self.config.maze.exit_x = size - 2
                    self.config.maze.exit_y = size - 2
                    self.audio_manager.play_ui_sound("click")

            for idx, spd in enumerate([3.0, 4.0, 5.2]):
                if pygame.Rect(260 + idx * 110, 230, 95, 34).collidepoint(mx, my):
                    self.config.maze.player_speed = spd
                    self.audio_manager.play_ui_sound("click")

            for idx, rad in enumerate([90, 135, 180]):
                if pygame.Rect(260 + idx * 110, 290, 95, 34).collidepoint(mx, my):
                    self.config.maze.flashlight_radius = rad
                    self.audio_manager.play_ui_sound("click")

        elif tab == "APARIÇÕES":
            for idx, dur in enumerate([120, 180, 250]):
                if pygame.Rect(260 + idx * 110, 160, 95, 34).collidepoint(mx, my):
                    for a in self.config.apparitions:
                        a.duration_ms = dur
                    self.audio_manager.play_ui_sound("click")

            for idx, sec in enumerate([5.0, 8.0, 14.0]):
                if pygame.Rect(260 + idx * 110, 215, 95, 34).collidepoint(mx, my):
                    for a in self.config.apparitions:
                        a.min_interval_sec = sec
                    self.audio_manager.play_ui_sound("click")

            # Sons para as aparições
            for idx, stype in enumerate(["glitch", "static", "whisper", "pop", "silent"]):
                if pygame.Rect(260 + idx * 95, 270, 85, 34).collidepoint(mx, my):
                    for a in self.config.apparitions:
                        a.sound_type = stype
                    self.audio_manager.start_preview(sound_type=stype if stype != "silent" else "glitch")

            # Chance de som (para sustos em silêncio)
            for idx, prob in enumerate([0.5, 0.8, 1.0]):
                if pygame.Rect(260 + idx * 110, 325, 95, 34).collidepoint(mx, my):
                    for a in self.config.apparitions:
                        a.sound_probability = prob
                    self.audio_manager.play_ui_sound("click")

        elif tab == "JUMPSCARE":
            for idx, dur in enumerate([1500, 2200, 3200]):
                if pygame.Rect(260 + idx * 110, 160, 95, 34).collidepoint(mx, my):
                    self.config.final_jumpscare.duration_ms = dur
                    self.audio_manager.play_ui_sound("click")

            # Tipo de som do susto principal
            for idx, stype in enumerate(["scream", "roar", "impact_screech", "distortion"]):
                if pygame.Rect(260 + idx * 110, 215, 100, 34).collidepoint(mx, my):
                    self.config.final_jumpscare.sound_type = stype
                    self.audio_manager.start_preview(sound_type=stype)

            if pygame.Rect(260, 270, 120, 34).collidepoint(mx, my):
                self.config.final_jumpscare.screen_shake = not self.config.final_jumpscare.screen_shake
                self.audio_manager.play_ui_sound("click")

            if pygame.Rect(260, 325, 120, 34).collidepoint(mx, my):
                self.config.final_jumpscare.zoom = not self.config.final_jumpscare.zoom
                self.audio_manager.play_ui_sound("click")

            # Botão de Teste Rápido
            if pygame.Rect(260, 380, 200, 36).collidepoint(mx, my):
                self.audio_manager.play_jumpscare(
                    sound_type=self.config.final_jumpscare.sound_type,
                    volume_mult=self.config.final_jumpscare.volume
                )

        elif tab == "ÁUDIO & BIBLIOTECA":
            # 1. Controles de Volume por Categoria (◀ / ▶)
            cats = [
                ("master_volume", 155),
                ("jumpscare_volume", 195),
                ("ambient_volume", 235),
                ("glitch_volume", 275),
                ("computer_volume", 315),
                ("interaction_volume", 355)
            ]
            for attr, y in cats:
                # Botão diminuir ◀
                if pygame.Rect(440, y, 32, 26).collidepoint(mx, my):
                    curr = getattr(self.config.audio, attr)
                    setattr(self.config.audio, attr, max(0.0, round(curr - 0.1, 2)))
                    self._sync_audio_volumes()
                    self.audio_manager.play_ui_sound("click")
                # Botão aumentar ▶
                if pygame.Rect(530, y, 32, 26).collidepoint(mx, my):
                    curr = getattr(self.config.audio, attr)
                    setattr(self.config.audio, attr, min(1.0, round(curr + 0.1, 2)))
                    self._sync_audio_volumes()
                    self.audio_manager.play_ui_sound("click")

            # 2. Seleção de Som para Testar
            for idx, (label, stype) in enumerate(self.preview_sounds):
                col = idx % 3
                row = idx // 3
                btn_rect = pygame.Rect(600 + col * 125, 160 + row * 40, 120, 32)
                if btn_rect.collidepoint(mx, my):
                    self.selected_preview_idx = idx
                    self.audio_manager.start_preview(sound_type=stype)

            # Botão Parar Pré-visualização
            if pygame.Rect(600, 290, 140, 36).collidepoint(mx, my):
                self.audio_manager.stop_preview()
                self.audio_manager.play_ui_sound("click")

            # Campo e botão de Importação
            if pygame.Rect(60, 420, 300, 32).collidepoint(mx, my):
                self.active_input_field = "import_audio"

            if pygame.Rect(375, 420, 120, 32).collidepoint(mx, my):
                self._apply_text_input("import_audio")

        elif tab == "DESKTOP & PASTAS":
            if pygame.Rect(260, 160, 260, 34).collidepoint(mx, my):
                self.active_input_field = "computer_name"

            # Alternar pasta perigosa ativa
            p = "Meus Documentos/Pessoal/nao_abra"
            if pygame.Rect(260, 220, 320, 36).collidepoint(mx, my):
                if p in self.config.dangerous_folders:
                    curr = self.config.dangerous_folders[p].status
                    self.config.dangerous_folders[p].status = "safe" if curr == "dangerous" else "dangerous"
                self.audio_manager.play_ui_sound("click")

            # Som da pasta perigosa
            for idx, stype in enumerate(["scream", "roar", "distortion", "whisper_glitch"]):
                if pygame.Rect(260 + idx * 110, 280, 100, 34).collidepoint(mx, my):
                    if p in self.config.dangerous_folders:
                        self.config.dangerous_folders[p].sound_type = stype
                    self.audio_manager.start_preview(sound_type=stype)

        elif tab == "CÓDIGO & FINAL":
            if pygame.Rect(260, 170, 260, 34).collidepoint(mx, my):
                self.active_input_field = "secret_code"

            if pygame.Rect(530, 170, 100, 34).collidepoint(mx, my):
                self._apply_text_input("secret_code")
                self.audio_manager.play_ui_sound("click")

        elif tab == "PERFIS":
            if pygame.Rect(260, 170, 260, 34).collidepoint(mx, my):
                self.active_input_field = "profile_name"

            if pygame.Rect(260, 230, 220, 38).collidepoint(mx, my):
                p_name = self.temp_inputs["profile_name"]
                self.save_manager.save_profile(p_name, self.config)
                self.status_message = f"Perfil '{p_name}' salvo com sucesso!"
                self.audio_manager.play_ui_sound("success")

            if pygame.Rect(260, 290, 220, 38).collidepoint(mx, my):
                default_cfg = GameConfig()
                self.config.from_dict(default_cfg.to_dict())
                self.status_message = "Configurações restauradas para os padrões!"
                self.audio_manager.play_ui_sound("click")

    def _sync_audio_volumes(self):
        self.audio_manager.set_volumes(
            master=self.config.audio.master_volume,
            jumpscare=self.config.audio.jumpscare_volume,
            ambient=self.config.audio.ambient_volume,
            glitch=self.config.audio.glitch_volume,
            computer=self.config.audio.computer_volume,
            interaction=self.config.audio.interaction_volume
        )

    def draw(self, surface: pygame.Surface):
        surface.fill((10, 14, 22))

        # Título
        title = self.title_font.render("PAINEL DO CRIADOR — PERSONALIZAÇÃO E ÁUDIO", True, (244, 63, 94))
        surface.blit(title, (30, 22))

        # Botão Voltar
        back_btn = pygame.Rect(self.screen_w - 140, 20, 110, 36)
        pygame.draw.rect(surface, (30, 41, 59), back_btn, border_radius=6)
        pygame.draw.rect(surface, (56, 189, 248), back_btn, 1, border_radius=6)
        b_txt = self.tab_font.render("◀ VOLTAR", True, (255, 255, 255))
        surface.blit(b_txt, (back_btn.x + 22, back_btn.y + 10))

        # Barra de Abas
        tab_w = (self.screen_w - 60) // len(self.tabs)
        for idx, tab_name in enumerate(self.tabs):
            is_active = (idx == self.current_tab_idx)
            tab_rect = pygame.Rect(30 + idx * tab_w, 75, tab_w - 4, 38)
            bg_col = (136, 19, 55) if is_active else (22, 30, 49)
            border_col = (244, 63, 94) if is_active else (51, 65, 85)

            pygame.draw.rect(surface, bg_col, tab_rect, border_radius=4)
            pygame.draw.rect(surface, border_col, tab_rect, 1, border_radius=4)

            txt = self.tab_font.render(tab_name, True, (255, 255, 255) if is_active else (148, 163, 184))
            surface.blit(txt, (tab_rect.x + (tab_rect.w - txt.get_width()) // 2, tab_rect.y + 11))

        # Conteúdo da Aba
        content_rect = pygame.Rect(30, 125, self.screen_w - 60, self.screen_h - 180)
        pygame.draw.rect(surface, (15, 23, 42), content_rect, border_radius=8)
        pygame.draw.rect(surface, (51, 65, 85), content_rect, 1, border_radius=8)

        tab = self.tabs[self.current_tab_idx]

        if tab == "LABIRINTO":
            self._draw_label(surface, "Tamanho do Labirinto:", 175)
            for idx, size in enumerate([15, 19, 25]):
                sel = (self.config.maze.cols == size)
                self._draw_choice_btn(surface, f"{size}x{size}", 260 + idx * 110, 170, sel)

            self._draw_label(surface, "Velocidade do Jogador:", 235)
            for idx, spd in enumerate([3.0, 4.0, 5.2]):
                sel = (abs(self.config.maze.player_speed - spd) < 0.2)
                labels = ["Lenta", "Média", "Rápida"]
                self._draw_choice_btn(surface, labels[idx], 260 + idx * 110, 230, sel)

            self._draw_label(surface, "Raio da Lanterna:", 295)
            for idx, rad in enumerate([90, 135, 180]):
                sel = (self.config.maze.flashlight_radius == rad)
                labels = ["Estreito", "Padrão", "Amplo"]
                self._draw_choice_btn(surface, labels[idx], 260 + idx * 110, 290, sel)

        elif tab == "APARIÇÕES":
            self._draw_label(surface, "Imagem Ativa:", 120)
            img_lbl = self.val_font.render(f"Arquivo: {self.config.apparitions[0].image_path}", True, (56, 189, 248))
            surface.blit(img_lbl, (260, 120))

            self._draw_label(surface, "Duração dos Flashes:", 165)
            for idx, dur in enumerate([120, 180, 250]):
                sel = (self.config.apparitions[0].duration_ms == dur)
                self._draw_choice_btn(surface, f"{dur} ms", 260 + idx * 110, 160, sel)

            self._draw_label(surface, "Intervalo de Segurança:", 220)
            for idx, sec in enumerate([5.0, 8.0, 14.0]):
                sel = (self.config.apparitions[0].min_interval_sec == sec)
                self._draw_choice_btn(surface, f"{int(sec)} seg", 260 + idx * 110, 215, sel)

            self._draw_label(surface, "Efeito Sonoro:", 275)
            current_stype = getattr(self.config.apparitions[0], "sound_type", "glitch")
            for idx, stype in enumerate(["glitch", "static", "whisper", "pop", "silent"]):
                sel = (current_stype == stype)
                self._draw_choice_btn(surface, stype.capitalize(), 260 + idx * 95, 270, sel, width=85)

            self._draw_label(surface, "Chance de Áudio:", 330)
            current_sprob = getattr(self.config.apparitions[0], "sound_probability", 0.8)
            for idx, prob in enumerate([0.5, 0.8, 1.0]):
                sel = (abs(current_sprob - prob) < 0.05)
                self._draw_choice_btn(surface, f"{int(prob*100)}%", 260 + idx * 110, 325, sel)

        elif tab == "JUMPSCARE":
            self._draw_label(surface, "Imagem do Jumpscare:", 120)
            img_lbl = self.val_font.render(f"Arquivo: {self.config.final_jumpscare.image_path}", True, (56, 189, 248))
            surface.blit(img_lbl, (260, 120))

            self._draw_label(surface, "Duração do Susto:", 165)
            for idx, dur in enumerate([1500, 2200, 3200]):
                sel = (self.config.final_jumpscare.duration_ms == dur)
                self._draw_choice_btn(surface, f"{dur/1000:.1f}s", 260 + idx * 110, 160, sel)

            self._draw_label(surface, "Tipo de Áudio:", 220)
            current_scare_snd = getattr(self.config.final_jumpscare, "sound_type", "scream")
            for idx, stype in enumerate(["scream", "roar", "impact_screech", "distortion"]):
                sel = (current_scare_snd == stype)
                labels = ["Grito", "Rugido", "Impacto", "Distorção"]
                self._draw_choice_btn(surface, labels[idx], 260 + idx * 110, 215, sel, width=100)

            self._draw_label(surface, "Tremor Violento:", 275)
            self._draw_choice_btn(surface, "LIGADO" if self.config.final_jumpscare.screen_shake else "DESL.", 260, 270, self.config.final_jumpscare.screen_shake)

            self._draw_label(surface, "Zoom na Imagem:", 330)
            self._draw_choice_btn(surface, "LIGADO" if self.config.final_jumpscare.zoom else "DESL.", 260, 325, self.config.final_jumpscare.zoom)

            self._draw_choice_btn(surface, "▶ TESTAR JUMPSCARE COMPLETO", 260, 380, False, width=240)

        elif tab == "ÁUDIO & BIBLIOTECA":
            # Volumes por categoria
            v_cats = [
                ("Volume Geral:", self.config.audio.master_volume, 155),
                ("Sustos (Jumpscares):", self.config.audio.jumpscare_volume, 195),
                ("Sons Ambientes:", self.config.audio.ambient_volume, 235),
                ("Flashes / Glitches:", self.config.audio.glitch_volume, 275),
                ("Computador Antigo:", self.config.audio.computer_volume, 315),
                ("Interações / Cliques:", self.config.audio.interaction_volume, 355)
            ]
            for label, val, y in v_cats:
                self._draw_label(surface, label, y + 4)
                # Botão ◀
                self._draw_choice_btn(surface, "◀", 440, y, False, width=32)
                # Valor
                v_txt = self.val_font.render(f"{int(val * 100)}%", True, (255, 255, 255))
                surface.blit(v_txt, (485, y + 5))
                # Botão ▶
                self._draw_choice_btn(surface, "▶", 530, y, False, width=32)

            # Biblioteca & Pré-Visualização
            lbl_lib = self.label_font.render("Pré-Visualizar Efeitos Sonoros:", True, (56, 189, 248))
            surface.blit(lbl_lib, (600, 135))

            for idx, (label, stype) in enumerate(self.preview_sounds):
                col = idx % 3
                row = idx // 3
                sel = (idx == self.selected_preview_idx)
                self._draw_choice_btn(surface, label, 600 + col * 125, 160 + row * 40, sel, width=120)

            self._draw_choice_btn(surface, "⏹ PARAR ÁUDIO", 600, 290, False, width=140)

            # Importação
            lbl_imp = self.label_font.render("Importar Arquivo de Áudio Externo (WAV, OGG, MP3):", True, (226, 232, 240))
            surface.blit(lbl_imp, (60, 395))
            self._draw_input_box(surface, "import_audio", 60, 420, 300)
            self._draw_choice_btn(surface, "IMPORTAR", 375, 420, False, width=110)

            # Documentação de fontes de áudio recomendadas
            ref_txt = self.small_font.render("Bancos recomendados: Freesound (freesound.org) | Pixabay (pixabay.com) | Mixkit (mixkit.co)", True, (148, 163, 184))
            surface.blit(ref_txt, (60, 465))

        elif tab == "DESKTOP & PASTAS":
            self._draw_label(surface, "Nome do Computador:", 165)
            self._draw_input_box(surface, "computer_name", 260, 160, 260)

            self._draw_label(surface, "Pasta 'nao_abra':", 225)
            p = "Meus Documentos/Pessoal/nao_abra"
            is_danger = (p in self.config.dangerous_folders and self.config.dangerous_folders[p].status == "dangerous")
            txt = "ESTADO: PERIGOSA (Jumpscare ao abrir)" if is_danger else "ESTADO: SEGURA"
            self._draw_choice_btn(surface, txt, 260, 220, is_danger, width=320)

            self._draw_label(surface, "Som do Susto da Pasta:", 285)
            curr_f_snd = getattr(self.config.dangerous_folders.get(p), "sound_type", "scream") if p in self.config.dangerous_folders else "scream"
            for idx, stype in enumerate(["scream", "roar", "distortion", "whisper"]):
                sel = (curr_f_snd == stype)
                labels = ["Grito", "Rugido", "Distorção", "Sussurro"]
                self._draw_choice_btn(surface, labels[idx], 260 + idx * 110, 280, sel, width=100)

        elif tab == "CÓDIGO & FINAL":
            self._draw_label(surface, "Código Secreto Final:", 175)
            self._draw_input_box(surface, "secret_code", 260, 170, 260)
            self._draw_choice_btn(surface, "SALVAR", 530, 170, False, width=100)

            doc_path_lbl = f"Documento Alvo: C:\\{self.config.investigation.target_document_path}"
            lbl_surf = self.val_font.render(doc_path_lbl, True, (148, 163, 184))
            surface.blit(lbl_surf, (260, 235))

        elif tab == "PERFIS":
            self._draw_label(surface, "Nome do Perfil:", 175)
            self._draw_input_box(surface, "profile_name", 260, 170, 260)

            self._draw_choice_btn(surface, "SALVAR PERFIL EM JSON", 260, 230, False, width=220)
            self._draw_choice_btn(surface, "RESTAURAR PADRÕES", 260, 290, False, width=220)

        # Mensagem de Status
        if self.status_message:
            s_surf = self.label_font.render(self.status_message, True, (56, 189, 248))
            surface.blit(s_surf, (50, self.screen_h - 90))

    def _draw_label(self, surface: pygame.Surface, text: str, y: int):
        lbl = self.label_font.render(text, True, (226, 232, 240))
        surface.blit(lbl, (60, y))

    def _draw_choice_btn(self, surface: pygame.Surface, text: str, x: int, y: int, is_selected: bool, width: int = 95):
        rect = pygame.Rect(x, y, width, 32)
        bg = (136, 19, 55) if is_selected else (30, 41, 59)
        border = (244, 63, 94) if is_selected else (51, 65, 85)
        pygame.draw.rect(surface, bg, rect, border_radius=4)
        pygame.draw.rect(surface, border, rect, 1, border_radius=4)
        t_surf = self.tab_font.render(text, True, (255, 255, 255) if is_selected else (203, 213, 225))
        surface.blit(t_surf, (rect.x + (rect.w - t_surf.get_width()) // 2, rect.y + 8))

    def _draw_input_box(self, surface: pygame.Surface, field_name: str, x: int, y: int, width: int):
        rect = pygame.Rect(x, y, width, 32)
        is_active = (self.active_input_field == field_name)
        border = (56, 189, 248) if is_active else (51, 65, 85)
        pygame.draw.rect(surface, (10, 15, 25), rect, border_radius=4)
        pygame.draw.rect(surface, border, rect, 2 if is_active else 1, border_radius=4)
        text = self.temp_inputs.get(field_name, "")
        t_surf = self.input_font.render(text, True, (255, 255, 255))
        surface.blit(t_surf, (rect.x + 8, rect.y + 6))

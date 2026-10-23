"""
THE LAST CORRIDOR — JOGO DE TERROR PSICOLÓGICO COM DESKTOP SIMULADO
Ponto de Entrada Principal da Aplicação Windows.
Coordena Máquina de Estados, Pygame Loop, Áudio, Labirinto, Jumpscares e Desktop Simulado.
"""

import sys
import os
import pygame
import random
from pathlib import Path
from typing import Optional

# Adiciona os diretórios ao PYTHONPATH para garantir importações estáveis
ROOT_DIR = Path(__file__).resolve().parent
PARENT_DIR = ROOT_DIR.parent
for p in (str(ROOT_DIR), str(PARENT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from core.config import GameConfig, get_app_base_dir
from core.save_manager import SaveManager
from core.asset_manager import AssetManager
from core.audio_manager import AudioManager
from game.maze import Maze
from game.player import Player
from game.atmosphere import AtmosphereRenderer
from game.apparition_manager import ApparitionManager
from game.jumpscare import JumpscareController
from game.game_states import GameState
from game.enemy import EnemyManager
from game.orb import MysteriousOrb
from desktop.virtual_computer import VirtualComputer
from ui.main_menu import MainMenu
from ui.settings import SettingsMenu
from ui.creator_panel import CreatorPanel


class TheLastCorridorGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("THE LAST CORRIDOR")

        # base_dir = onde estão os ASSETS (dentro de _internal/ no .exe, ou raiz do projeto no dev)
        self.base_dir = get_app_base_dir()

        # save_dir = onde salvar perfis/saves (junto ao .exe para ser gravável; igual ao base_dir no dev)
        if getattr(sys, "frozen", False):
            self.save_dir = Path(sys.executable).parent
        else:
            self.save_dir = self.base_dir

        # Gerenciador de Salvamento e Configurações
        self.save_manager = SaveManager(base_dir=self.save_dir)
        self.config = self.save_manager.get_or_create_default_config()

        # Dimensões da Janela
        self.screen_w = self.config.display.width
        self.screen_h = self.config.display.height

        flags = pygame.DOUBLEBUF
        if self.config.display.fullscreen:
            flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), flags)
        self.clock = pygame.time.Clock()

        # Gerenciadores de Mídia (usam base_dir para ler assets)
        self.asset_manager = AssetManager(base_dir=self.base_dir)
        self.audio_manager = AudioManager(base_dir=self.base_dir)
        self.audio_manager.set_volumes(
            self.config.audio.master_volume,
            jumpscare=self.config.audio.jumpscare_volume,
            ambient=self.config.audio.ambient_volume,
            glitch=self.config.audio.glitch_volume,
            computer=self.config.audio.computer_volume,
            interaction=self.config.audio.interaction_volume,
            footstep=getattr(self.config.audio, "footstep_volume", 1.0),
            muted=self.config.audio.audio_muted
        )

        # Estado da Partida
        self.current_state = GameState.MAIN_MENU
        self.running = True

        # Segunda Fase: Inimigos e Orbe
        self.maze2: Optional[Maze] = None
        self.player2: Optional[Player] = None
        self.atmosphere2: Optional[AtmosphereRenderer] = None
        self.enemy_manager: Optional[EnemyManager] = None
        self.mysterious_orb: Optional[MysteriousOrb] = None
        self.orb_jumpscare_timer: float = 0.0
        self.orb_jumpscare_duration: float = 3.0
        self.orb_jumpscare_image_path: str = "assets/images/jumpscare_orbe.png"
        self.phase2_static_audio_path: str = "assets/audio/glitches/static_noise.wav"

        # Intermissão: "Você está bem?" com choro acelerado
        self.intermission_timer: float = 0.0
        self.intermission_duration: float = 10.0
        self.intermission_text: str = "você está bem?"
        self.choro_sound_path: str = "assets/audio/ambience/choro_acelerado.wav"

        # Inicialização dos Sistemas de Jogo
        self._init_maze_phase()
        self._init_desktop_phase()
        self._init_ui_screens()

    def _init_maze_phase(self):
        """Inicializa ou reinicializa a fase do labirinto."""
        self.maze = Maze(
            cols=self.config.maze.cols,
            rows=self.config.maze.rows,
            cell_size=self.config.maze.cell_size
        )

        start_px, start_py = self.maze.get_world_pos(*self.maze.start_pos)
        self.player = Player(
            x=start_px,
            y=start_py,
            speed=self.config.maze.player_speed,
            radius=self.config.maze.cell_size * 0.32
        )

        self.atmosphere = AtmosphereRenderer(
            screen_w=self.screen_w,
            screen_h=self.screen_h,
            base_radius=self.config.maze.flashlight_radius
        )

        self.apparition_mgr = ApparitionManager(
            apparitions=self.config.apparitions,
            asset_manager=self.asset_manager,
            audio_manager=self.audio_manager
        )

        self.jumpscare_ctrl = JumpscareController(
            config=self.config.final_jumpscare,
            asset_manager=self.asset_manager,
            audio_manager=self.audio_manager
        )

    def _init_phase2(self):
        """Inicializa a segunda fase com labirinto ampliado, nevoeiro mais denso e inimigos."""
        self.maze2 = Maze(
            cols=21,
            rows=21,
            cell_size=self.config.maze.cell_size
        )
        start_px, start_py = self.maze2.get_world_pos(*self.maze2.start_pos)
        self.player2 = Player(
            x=start_px,
            y=start_py,
            speed=self.config.maze.player_speed * 0.9,
            radius=self.config.maze.cell_size * 0.32
        )
        # Inimigos patrulheiros
        self.enemy_manager = EnemyManager(self.maze2, count=3)

        # Orbe na saída do labirinto 2
        ex, ey = self.maze2.exit_pos
        orb_px, orb_py = self.maze2.get_world_pos(ex, ey)
        self.mysterious_orb = MysteriousOrb(orb_px, orb_py, self.audio_manager)

        # Atmosfera com raio de visão mais estreito
        self.atmosphere2 = AtmosphereRenderer(
            screen_w=self.screen_w,
            screen_h=self.screen_h,
            base_radius=int(self.config.maze.flashlight_radius * 0.75)
        )

    def _init_desktop_phase(self):
        """Inicializa o computador antigo simulado."""
        self.virtual_computer = VirtualComputer(
            desktop_cfg=self.config.desktop,
            investigation_cfg=self.config.investigation,
            dangerous_folders=self.config.dangerous_folders,
            filesystem_tree=self.config.filesystem_tree,
            asset_manager=self.asset_manager,
            audio_manager=self.audio_manager,
            on_victory=self.on_victory,
            screen_w=self.screen_w,
            screen_h=self.screen_h
        )

    def _init_ui_screens(self):
        """Inicializa os menus e telas de navegação."""
        has_save = self.save_manager.load_game_state() is not None

        self.main_menu = MainMenu(
            audio_manager=self.audio_manager,
            on_play=self.start_new_game,
            on_continue=self.continue_saved_game,
            on_settings=lambda: self.change_state(GameState.SETTINGS),
            on_customize=lambda: self.change_state(GameState.CREATOR_PANEL),
            on_test_jumpscare=self.test_jumpscare,
            on_exit=self.quit_game,
            has_save_game=has_save,
            screen_w=self.screen_w,
            screen_h=self.screen_h
        )

        self.settings_menu = SettingsMenu(
            config=self.config,
            audio_manager=self.audio_manager,
            on_back=lambda: self.change_state(GameState.MAIN_MENU),
            screen_w=self.screen_w,
            screen_h=self.screen_h
        )

        self.creator_panel = CreatorPanel(
            config=self.config,
            save_manager=self.save_manager,
            audio_manager=self.audio_manager,
            on_back=self.on_creator_panel_back,
            screen_w=self.screen_w,
            screen_h=self.screen_h
        )

    def change_state(self, new_state: GameState):
        self.current_state = new_state
        if new_state == GameState.MAIN_MENU:
            has_save = self.save_manager.load_game_state() is not None
            self.main_menu.set_has_save_game(has_save)

    def start_new_game(self):
        """Inicia uma partida limpa no labirinto."""
        self._init_maze_phase()
        self.apparition_mgr.reset()
        self.audio_manager.start_ambient_drone()
        self.change_state(GameState.MAZE)
        self.save_current_state()

    def continue_saved_game(self):
        """Continua a partida do ponto onde o jogador parou."""
        saved = self.save_manager.load_game_state()
        if not saved:
            self.start_new_game()
            return

        stage = saved.get("stage", "maze")
        if stage == "desktop":
            self.audio_manager.stop_ambient_drone()
            self.virtual_computer.start_boot()
            self.change_state(GameState.DESKTOP)
        else:
            self._init_maze_phase()
            self.player.x = saved.get("player_x", self.player.x)
            self.player.y = saved.get("player_y", self.player.y)
            self.audio_manager.start_ambient_drone()
            self.change_state(GameState.MAZE)

    def test_jumpscare(self):
        """Testa o susto principal isoladamente."""
        self.jumpscare_ctrl.trigger()
        self.change_state(GameState.JUMPSCARE_TEST)

    def on_creator_panel_back(self):
        """Aplica mudanças de configuração ao sair do painel do criador."""
        self.save_manager.save_profile("default", self.config)
        self._init_maze_phase()
        self._init_desktop_phase()
        self.change_state(GameState.MAIN_MENU)

    def on_victory(self):
        """Chamado quando o jogador decifra o código."""
        self.save_manager.clear_game_state()
        self.audio_manager.stop_ambient_drone()
        self.audio_manager.play_ui_sound("success")
        self.change_state(GameState.VICTORY)

    def save_current_state(self):
        """Persiste o progresso atual."""
        state_data = {
            "stage": "desktop" if self.current_state == GameState.DESKTOP else "maze",
            "player_x": self.player.x,
            "player_y": self.player.y,
            "steps": self.player.steps_count
        }
        self.save_manager.save_game_state(state_data)

    def quit_game(self):
        self.running = False

    # --- Loop Principal ---

    def run(self):
        while self.running:
            dt = self.clock.tick(self.config.display.fps) / 1000.0

            # 1. Tratar Eventos Globais
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    # Alternar Tela Cheia
                    self.config.display.fullscreen = not self.config.display.fullscreen
                    flags = pygame.DOUBLEBUF | (pygame.FULLSCREEN if self.config.display.fullscreen else 0)
                    self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), flags)

                else:
                    self._dispatch_event(event)

            # 2. Atualizar Lógica de Acordo com o Estado
            self._update(dt)

            # 3. Renderizar Tela de Acordo com o Estado
            self._render()

            # 4. Aplicar Filtro CRT Opcional
            if self.config.display.crt_scanlines:
                crt = self.asset_manager.get_crt_overlay(self.screen_w, self.screen_h)
                self.screen.blit(crt, (0, 0))

            pygame.display.flip()

        pygame.quit()
        sys.exit(0)

    def _dispatch_event(self, event: pygame.event.Event):
        state = self.current_state

        if state == GameState.MAIN_MENU:
            self.main_menu.handle_event(event)

        elif state == GameState.SETTINGS:
            self.settings_menu.handle_event(event)

        elif state == GameState.CREATOR_PANEL:
            self.creator_panel.handle_event(event)

        elif state == GameState.MAZE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.save_current_state()
                self.audio_manager.stop_ambient_drone()
                self.change_state(GameState.MAIN_MENU)

        elif state == GameState.INTERMISSION_CRY:
            pass  # Não permite pular a cena do choro

        elif state == GameState.PHASE2:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.audio_manager.stop_ambient_drone()
                    self.change_state(GameState.MAIN_MENU)
                elif event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                    if self.mysterious_orb and self.player2:
                        collected = self.mysterious_orb.try_collect(self.player2.x, self.player2.y)
                        if collected:
                            self.audio_manager.stop_ambient_drone()
                            # Jumpscare da segunda fase: toca exclusivamente o ruído estático
                            self.audio_manager.play_jumpscare(
                                path_str=self.phase2_static_audio_path,
                                sound_type="static",
                                volume_mult=1.0
                            )
                            self.orb_jumpscare_timer = self.orb_jumpscare_duration
                            self.change_state(GameState.ORB_JUMPSCARE)

        elif state == GameState.ORB_JUMPSCARE:
            pass  # Não permite pular a cena da orbe

        elif state == GameState.DESKTOP:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.save_current_state()
                self.change_state(GameState.MAIN_MENU)
            else:
                self.virtual_computer.handle_event(event)

        elif state == GameState.VICTORY:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.change_state(GameState.MAIN_MENU)

        elif state == GameState.JUMPSCARE_TEST:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.jumpscare_ctrl.is_active = False
                self.change_state(GameState.MAIN_MENU)

    def _update(self, dt: float):
        state = self.current_state

        if state == GameState.MAZE:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys, self.maze, self.audio_manager, dt=1.0)

            # Verificar região atual para aparições
            gx, gy = self.player.get_grid_pos(self.maze.cell_size)
            reg = self.maze.get_region_tag(gx, gy)

            # Atualizar sistema de sustos relâmpago
            self.apparition_mgr.update(self.player.steps_count, reg, dt)

            # Verificar se alcançou a saída (disparo do Jumpscare Final!)
            ex, ey = self.maze.exit_pos
            if gx == ex and gy == ey:
                self.audio_manager.stop_ambient_drone()
                self.jumpscare_ctrl.trigger()
                self.change_state(GameState.FINAL_JUMPSCARE)

        elif state == GameState.FINAL_JUMPSCARE:
            is_active = self.jumpscare_ctrl.update()
            if not is_active:
                # Transição para a tela de intermissão ("você está bem?") com choro acelerado alto
                self.intermission_timer = self.intermission_duration
                # Toca o choro acelerado e alto
                choro_snd = self.audio_manager.load_sound(self.choro_sound_path, fallback_key="whisper")
                if choro_snd:
                    ch_amb = pygame.mixer.Channel(AudioManager.CH_AMBIENT)
                    choro_snd.set_volume(1.0)
                    ch_amb.play(choro_snd, loops=-1)
                self.change_state(GameState.INTERMISSION_CRY)

        elif state == GameState.INTERMISSION_CRY:
            self.intermission_timer -= dt
            if self.intermission_timer <= 0:
                # Conclui os 10 segundos de choro e inicia a Fase 2
                self.audio_manager.stop_ambient_drone()
                self._init_phase2()
                self.audio_manager.start_ambient_drone("maze")
                self.change_state(GameState.PHASE2)

        elif state == GameState.PHASE2:
            if self.player2 and self.maze2 and self.enemy_manager and self.mysterious_orb:
                keys = pygame.key.get_pressed()
                self.player2.handle_input(keys, self.maze2, self.audio_manager, dt=1.0)
                
                # Atualizar orbe e proximidade
                self.mysterious_orb.update(self.player2.x, self.player2.y, dt)
                
                # Atualizar inimigos e testar captura
                caught = self.enemy_manager.update(self.player2.x, self.player2.y, dt)
                if caught:
                    self.enemy_manager.reset_caught()
                    # Reposiciona jogador no início da fase 2 e dispara rugido de choque
                    spx, spy = self.maze2.get_world_pos(*self.maze2.start_pos)
                    self.player2.x = spx
                    self.player2.y = spy
                    self.audio_manager.play_jumpscare(sound_type="roar", volume_mult=0.85)

        elif state == GameState.ORB_JUMPSCARE:
            self.orb_jumpscare_timer -= dt
            if self.orb_jumpscare_timer <= 0:
                # Transição para o computador antigo simulado
                self.save_current_state()
                self.virtual_computer.start_boot()
                self.change_state(GameState.DESKTOP)

        elif state == GameState.JUMPSCARE_TEST:
            is_active = self.jumpscare_ctrl.update()
            if not is_active:
                self.change_state(GameState.MAIN_MENU)

        elif state == GameState.DESKTOP:
            self.virtual_computer.update(dt)

    def _render(self):
        state = self.current_state

        if state == GameState.MAIN_MENU:
            self.main_menu.draw(self.screen)

        elif state == GameState.SETTINGS:
            self.settings_menu.draw(self.screen)

        elif state == GameState.CREATOR_PANEL:
            self.creator_panel.draw(self.screen)

        elif state == GameState.MAZE:
            cam_offset = self.atmosphere.get_camera_offset(self.player.x, self.player.y)
            # 1. Renderiza labirinto
            self.atmosphere.render_maze(self.screen, self.maze, cam_offset)
            # 2. Renderiza jogador
            self.player.draw(self.screen, cam_offset)
            # 3. Aplica escuridão e lanterna
            screen_px = int(self.player.x - cam_offset[0])
            screen_py = int(self.player.y - cam_offset[1])
            self.atmosphere.render_flashlight_and_darkness(
                self.screen,
                screen_px,
                screen_py,
                reduce_flashes=self.config.display.reduce_flashes
            )
            # 4. Renderiza aparições relâmpago por cima
            self.apparition_mgr.draw(
                self.screen,
                self.screen_w,
                self.screen_h,
                reduce_flashes=self.config.display.reduce_flashes
            )

        elif state in (GameState.FINAL_JUMPSCARE, GameState.JUMPSCARE_TEST):
            self.screen.fill((0, 0, 0))
            self.jumpscare_ctrl.draw(
                self.screen,
                self.screen_w,
                self.screen_h,
                reduce_flashes=self.config.display.reduce_flashes,
                reduce_shakes=self.config.display.reduce_shakes
            )

        elif state == GameState.INTERMISSION_CRY:
            self.screen.fill((0, 0, 0))
            # Fundo preto total com a frase "você está bem?"
            # Efeito de tremor e pulsação sutil na fonte
            import math
            pulse = 0.8 + 0.2 * math.sin((10.0 - self.intermission_timer) * 3.5)
            alpha_color = int(220 * pulse)
            try:
                msg_font = pygame.font.SysFont("Courier New", 26, bold=True)
                t_surf = msg_font.render("você está bem?", True, (alpha_color, alpha_color, alpha_color))
                # Pequeno glitch visual ocasional
                gx, gy = 0, 0
                if random.random() < 0.12:
                    gx = random.randint(-4, 4)
                    gy = random.randint(-2, 2)
                self.screen.blit(t_surf, ((self.screen_w - t_surf.get_width()) // 2 + gx, (self.screen_h - t_surf.get_height()) // 2 + gy))
            except Exception:
                pass

        elif state == GameState.PHASE2:
            if self.player2 and self.maze2 and self.atmosphere2:
                cam_offset = self.atmosphere2.get_camera_offset(self.player2.x, self.player2.y)
                self.atmosphere2.render_maze(self.screen, self.maze2, cam_offset)
                
                # Inimigos
                if self.enemy_manager:
                    self.enemy_manager.draw(self.screen, cam_offset)
                
                # Orbe misteriosa
                if self.mysterious_orb:
                    self.mysterious_orb.draw(self.screen, cam_offset)
                
                # Jogador
                self.player2.draw(self.screen, cam_offset)
                
                # Lanterna mais restrita
                screen_px = int(self.player2.x - cam_offset[0])
                screen_py = int(self.player2.y - cam_offset[1])
                self.atmosphere2.render_flashlight_and_darkness(
                    self.screen,
                    screen_px,
                    screen_py,
                    reduce_flashes=self.config.display.reduce_flashes
                )
                
                # HUD da Fase 2
                self._render_phase2_hud()

        elif state == GameState.ORB_JUMPSCARE:
            self.screen.fill((0, 0, 0))
            # Rosto macabro do jumpscare da orbe em tela cheia
            img = self.asset_manager.load_image(
                self.orb_jumpscare_image_path,
                target_size=(self.screen_w, self.screen_h),
                fallback_type="jumpscare"
            )
            self.screen.blit(img, (0, 0))
            # Efeito de interferência e TV quebrada
            for _ in range(6):
                slice_y = random.randint(0, self.screen_h - 18)
                slice_h = random.randint(4, 16)
                offset = random.randint(-28, 28)
                rect = pygame.Rect(0, slice_y, self.screen_w, slice_h)
                try:
                    sub = self.screen.subsurface(rect).copy()
                    self.screen.blit(sub, (offset, slice_y))
                except Exception:
                    pass

        elif state == GameState.DESKTOP:
            self.virtual_computer.draw(
                self.screen,
                reduce_flashes=self.config.display.reduce_flashes,
                reduce_shakes=self.config.display.reduce_shakes
            )

        elif state == GameState.VICTORY:
            self._render_victory_screen()

    def _render_victory_screen(self):
        """Tela de conclusão da experiência de terror."""
        self.screen.fill((4, 8, 16))

        title_font = pygame.font.SysFont("Georgia", 36, bold=True)
        body_font = pygame.font.SysFont("Courier New", 14)
        hint_font = pygame.font.SysFont("Segoe UI", 12)

        t_surf = title_font.render("CONEXÃO FINALIZADA", True, (56, 189, 248))
        self.screen.blit(t_surf, ((self.screen_w - t_surf.get_width()) // 2, 140))

        lines = self.config.investigation.victory_message.split("\n")
        y = 240
        for l in lines:
            l_surf = body_font.render(l, True, (226, 232, 240))
            self.screen.blit(l_surf, ((self.screen_w - l_surf.get_width()) // 2, y))
            y += 28

        h_surf = hint_font.render("Pressione qualquer tecla para retornar ao Menu Principal.", True, (148, 163, 184))
        self.screen.blit(h_surf, ((self.screen_w - h_surf.get_width()) // 2, self.screen_h - 100))

    def _render_phase2_hud(self):
        """HUD discreto da segunda fase."""
        try:
            font = pygame.font.SysFont("Courier New", 13, bold=True)
            txt = font.render("FASE 2 — A ORBE MISTERIOSA", True, (200, 70, 70))
            self.screen.blit(txt, (14, 14))
            hint = font.render("[WASD] Mover | [E] Interagir com a Orbe | Cuidado com as Sombras", True, (120, 120, 120))
            self.screen.blit(hint, (14, self.screen_h - 26))
        except Exception:
            pass


def main():
    game = TheLastCorridorGame()
    game.run()


if __name__ == "__main__":
    main()

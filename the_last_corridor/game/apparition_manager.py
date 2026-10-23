"""
Gerenciador de Aparições e Flashes Macabros de THE LAST CORRIDOR.
Controla sustos relâmpago durante o labirinto respeitando intervalos mínimos, distância percorrida,
probabilidades, regiões e evitando sobreposição de efeitos.
"""

import pygame
import time
import random
from typing import List, Optional, Tuple, Dict
try:
    from core.config import ApparitionItem
    from core.asset_manager import AssetManager
    from core.audio_manager import AudioManager
except ImportError:
    from the_last_corridor.core.config import ApparitionItem
    from the_last_corridor.core.asset_manager import AssetManager
    from the_last_corridor.core.audio_manager import AudioManager


class ApparitionManager:
    def __init__(self, apparitions: List[ApparitionItem], asset_manager: AssetManager, audio_manager: AudioManager):
        self.apparitions = apparitions
        self.asset_manager = asset_manager
        self.audio_manager = audio_manager

        # Estado atual de exibição
        self.current_scare: Optional[ApparitionItem] = None
        self.scare_start_time: float = 0.0
        self.last_scare_time: float = 0.0
        self.last_scare_step_count: int = 0
        self.occurrences_count: Dict[str, int] = {}

    def reset(self):
        """Reinicia estado do gerenciador para nova partida."""
        self.current_scare = None
        self.scare_start_time = 0.0
        self.last_scare_time = time.time()  # Dá alguns segundos de calma no início
        self.last_scare_step_count = 0
        self.occurrences_count.clear()

    def update(self, player_steps: int, current_region: str, dt: float) -> bool:
        """
        Avalia se uma nova aparição deve ser disparada e finaliza aparições expiradas.
        Retorna True se uma aparição estiver ativa na tela agora.
        """
        now = time.time()

        # 1. Se já existe uma aparição ativa, verificar se o tempo acabou
        if self.current_scare is not None:
            elapsed_ms = (now - self.scare_start_time) * 1000.0
            if elapsed_ms >= self.current_scare.duration_ms:
                self.current_scare = None
                self.last_scare_time = now
            return self.current_scare is not None

        # 2. Se não há aparições configuradas, nada a fazer
        if not self.apparitions:
            return False

        # 3. Filtrar aparições elegíveis
        eligible: List[ApparitionItem] = []
        for app in self.apparitions:
            # Verifica limite de ocorrências
            count = self.occurrences_count.get(app.id, 0)
            if app.max_occurrences != -1 and count >= app.max_occurrences:
                continue

            # Verifica região
            if app.region_tag != "all" and app.region_tag != current_region:
                continue

            # Verifica intervalo mínimo de tempo
            if (now - self.last_scare_time) < app.min_interval_sec:
                continue

            # Verifica distância mínima percorrida
            steps_since_last = player_steps - self.last_scare_step_count
            if steps_since_last < app.min_distance_steps:
                continue

            eligible.append(app)

        if not eligible:
            return False

        # 4. Avaliar probabilidade (sorteio aleatório por segundo)
        chosen = random.choice(eligible)
        # Sorteio com base na probabilidade
        if random.random() < (chosen.probability * dt * 0.8):
            self.trigger_apparition(chosen, player_steps)
            return True

        return False

    def trigger_apparition(self, item: ApparitionItem, player_steps: int):
        """Dispara imediatamente uma aparição macabra."""
        self.current_scare = item
        self.scare_start_time = time.time()
        self.last_scare_step_count = player_steps
        self.occurrences_count[item.id] = self.occurrences_count.get(item.id, 0) + 1

        # Tocar som de aparição associado ou som procedural padrão
        sound_type = getattr(item, "sound_type", "glitch")
        sound_prob = getattr(item, "sound_probability", 0.8)
        self.audio_manager.play_apparition(
            path_str=item.sound_path,
            sound_type=sound_type,
            probability=sound_prob
        )

    def draw(self, surface: pygame.Surface, screen_w: int, screen_h: int, reduce_flashes: bool = False):
        """Renderiza a aparição ativa na tela."""
        if self.current_scare is None:
            return

        item = self.current_scare
        img = self.asset_manager.load_image(
            item.image_path,
            target_size=(screen_w, screen_h) if item.position_mode == "fullscreen" else (480, 480),
            fallback_type="apparition"
        )

        # Intensidade / Transparência
        alpha = int(255 * item.intensity)
        if reduce_flashes:
            alpha = min(alpha, 160)

        img_to_draw = img.copy()
        img_to_draw.set_alpha(alpha)

        if item.position_mode == "fullscreen":
            surface.blit(img_to_draw, (0, 0))
        else:
            # Centralizada com leve deslocamento estocástico para susto
            offset_x = random.randint(-8, 8) if not reduce_flashes else 0
            offset_y = random.randint(-8, 8) if not reduce_flashes else 0
            cx = (screen_w - img_to_draw.get_width()) // 2 + offset_x
            cy = (screen_h - img_to_draw.get_height()) // 2 + offset_y
            surface.blit(img_to_draw, (cx, cy))

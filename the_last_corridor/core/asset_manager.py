"""
Gerenciador de Recursos Visuais e Texturas de THE LAST CORRIDOR.
Carrega imagens personalizadas (PNG, JPG, JPEG, BMP, WEBP) e gera gráficos de fallback
macabros e ícones retrô de computador caso os arquivos não existam.
"""

import pygame
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import math
import random
from .config import get_app_base_dir


class AssetManager:
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            self.base_dir = get_app_base_dir()
        else:
            self.base_dir = Path(base_dir)

        self.images_dir = self.base_dir / "assets" / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        self._image_cache: Dict[str, pygame.Surface] = {}
        self._thumbnail_cache: Dict[str, pygame.Surface] = {}
        self._crt_surface: Optional[pygame.Surface] = None

    def load_image(self, path_str: str, target_size: Optional[Tuple[int, int]] = None, fallback_type: str = "jumpscare") -> pygame.Surface:
        """Carrega uma imagem do disco ou gera uma textura assustadora procedural se não existir."""
        cache_key = f"{path_str}_{target_size}_{fallback_type}"
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        surf = None
        if path_str:
            p = Path(path_str)
            if not p.is_absolute():
                candidates = [
                    self.base_dir / p,
                    self.images_dir / p.name,
                    self.images_dir / p,
                    self.base_dir / "assets" / "images" / p.name,
                    self.base_dir / "_internal" / "assets" / "images" / p.name,
                    Path(sys.executable).parent / "assets" / "images" / p.name if getattr(sys, "frozen", False) else None,
                    Path(sys.executable).parent / "_internal" / "assets" / "images" / p.name if getattr(sys, "frozen", False) else None,
                ]
                for cand in candidates:
                    if cand and cand.exists() and cand.is_file():
                        p = cand
                        break

            if p.exists() and p.is_file():
                try:
                    raw_img = pygame.image.load(str(p))
                    if pygame.display.get_surface():
                        loaded = raw_img.convert_alpha()
                    else:
                        loaded = raw_img

                    if target_size:
                        surf = pygame.transform.smoothscale(loaded, target_size)
                    else:
                        surf = loaded
                except Exception as e:
                    print(f"[AssetManager] Falha ao carregar imagem '{path_str}': {e}. Usando fallback.")

        if surf is None:
            # Gerar imagem procedural de fallback
            size = target_size or (800, 600)
            if fallback_type == "jumpscare":
                surf = self._create_procedural_jumpscare(size[0], size[1])
            elif fallback_type == "apparition":
                surf = self._create_procedural_apparition(size[0], size[1])
            elif fallback_type == "wallpaper":
                surf = self._create_procedural_wallpaper(size[0], size[1])
            elif fallback_type == "folder":
                surf = self._create_icon_folder(size[0], size[1])
            elif fallback_type == "file":
                surf = self._create_icon_file(size[0], size[1])
            elif fallback_type == "danger_folder":
                surf = self._create_icon_danger_folder(size[0], size[1])
            else:
                surf = self._create_procedural_jumpscare(size[0], size[1])

        self._image_cache[cache_key] = surf
        return surf

    def get_thumbnail(self, path_str: str, size: Tuple[int, int] = (64, 64), fallback_type: str = "jumpscare") -> pygame.Surface:
        """Retorna uma miniatura para a biblioteca e painel do criador."""
        thumb_key = f"thumb_{path_str}_{size}"
        if thumb_key in self._thumbnail_cache:
            return self._thumbnail_cache[thumb_key]

        full_img = self.load_image(path_str, target_size=None, fallback_type=fallback_type)
        thumb = pygame.transform.smoothscale(full_img, size)
        self._thumbnail_cache[thumb_key] = thumb
        return thumb

    def validate_image_file(self, path_str: str) -> Tuple[bool, str]:
        """Valida se o arquivo de imagem é suportado e pode ser aberto."""
        try:
            p = Path(path_str)
            if not p.exists() or not p.is_file():
                return False, "Arquivo não encontrado."
            ext = p.suffix.lower()
            if ext not in [".png", ".jpg", ".jpeg", ".bmp", ".webp"]:
                return False, f"Formato '{ext}' não suportado (use PNG, JPG, BMP ou WEBP)."
            # Teste de carregamento
            test_surf = pygame.image.load(str(p))
            if test_surf.get_width() <= 0 or test_surf.get_height() <= 0:
                return False, "Dimensões de imagem inválidas."
            return True, "Imagem válida."
        except Exception as e:
            return False, f"Erro ao decodificar imagem: {e}"

    def get_crt_overlay(self, width: int, height: int) -> pygame.Surface:
        """Gera ou reaproveita uma máscara de linhas de varredura CRT e vinheta retrô."""
        if self._crt_surface is not None and self._crt_surface.get_size() == (width, height):
            return self._crt_surface

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        # Linhas de varredura horizontais
        for y in range(0, height, 3):
            pygame.draw.line(overlay, (0, 0, 0, 45), (0, y), (width, y), 1)

        # Vinheta nas bordas
        center_x, center_y = width / 2, height / 2
        max_dist = math.hypot(center_x, center_y)

        # Gradiente simples de vinheta nos 4 cantos
        corner_size = 180
        for corner in [(0, 0), (width, 0), (0, height), (width, height)]:
            corner_surf = pygame.Surface((corner_size, corner_size), pygame.SRCALPHA)
            for r in range(corner_size, 0, -4):
                alpha = int((1.0 - (r / corner_size)) * 90)
                pygame.draw.circle(corner_surf, (0, 0, 0, alpha), (0 if corner[0] == 0 else corner_size, 0 if corner[1] == 0 else corner_size), r)
            overlay.blit(corner_surf, (corner[0] - (corner_size if corner[0] > 0 else 0), corner[1] - (corner_size if corner[1] > 0 else 0)))

        self._crt_surface = overlay
        return overlay

    # --- Geradores Procedurais de Terror ---

    def _create_procedural_jumpscare(self, width: int, height: int) -> pygame.Surface:
        """Gera um rosto fantasmagórico bizarro e aterrorizante de alto contraste."""
        surf = pygame.Surface((width, height))
        surf.fill((6, 2, 8))

        cx, cy = width // 2, height // 2
        head_w = int(width * 0.35)
        head_h = int(height * 0.48)

        # Cabeça pálida cadavérica
        head_rect = pygame.Rect(cx - head_w // 2, cy - head_h // 2, head_w, head_h)
        pygame.draw.ellipse(surf, (190, 195, 205), head_rect)

        # Sombreamento cadavérico
        inner_rect = head_rect.inflate(-20, -25)
        pygame.draw.ellipse(surf, (140, 145, 155), inner_rect)

        # Órbitas oculares vazias e profundas
        eye_y = cy - int(head_h * 0.12)
        eye_spacing = int(head_w * 0.22)
        eye_r_w = int(head_w * 0.14)
        eye_r_h = int(head_h * 0.16)

        left_eye = pygame.Rect(cx - eye_spacing - eye_r_w, eye_y - eye_r_h // 2, eye_r_w * 2, eye_r_h)
        right_eye = pygame.Rect(cx + eye_spacing - eye_r_w, eye_y - eye_r_h // 2, eye_r_w * 2, eye_r_h)
        pygame.draw.ellipse(surf, (10, 0, 2), left_eye)
        pygame.draw.ellipse(surf, (10, 0, 2), right_eye)

        # Pupilas vermelhas sinistras e dilatadas
        pygame.draw.circle(surf, (220, 20, 30), (cx - eye_spacing, eye_y), max(2, int(eye_r_w * 0.35)))
        pygame.draw.circle(surf, (220, 20, 30), (cx + eye_spacing, eye_y), max(2, int(eye_r_w * 0.35)))
        pygame.draw.circle(surf, (255, 255, 255), (cx - eye_spacing, eye_y), max(1, int(eye_r_w * 0.12)))
        pygame.draw.circle(surf, (255, 255, 255), (cx + eye_spacing, eye_y), max(1, int(eye_r_w * 0.12)))

        # Boca aberta em um grito silencioso e alongado
        mouth_y = cy + int(head_h * 0.22)
        mouth_w = int(head_w * 0.28)
        mouth_h = int(head_h * 0.28)
        mouth_rect = pygame.Rect(cx - mouth_w // 2, mouth_y - mouth_h // 2, mouth_w, mouth_h)
        pygame.draw.ellipse(surf, (15, 0, 5), mouth_rect)

        # Dentes irregulares e pontiagudos
        for i in range(-mouth_w // 2 + 6, mouth_w // 2 - 6, 8):
            pygame.draw.line(surf, (220, 220, 200), (cx + i, mouth_y - mouth_h // 2 + 3), (cx + i, mouth_y - mouth_h // 2 + 10), 2)
            pygame.draw.line(surf, (220, 220, 200), (cx + i, mouth_y + mouth_h // 2 - 3), (cx + i, mouth_y + mouth_h // 2 - 10), 2)

        # Ruído estático de vídeo corrompido
        for _ in range(350):
            rx = random.randint(0, width - 1)
            ry = random.randint(0, height - 1)
            c = random.choice([(255, 0, 0), (255, 255, 255), (80, 0, 0), (0, 0, 0)])
            surf.set_at((rx, ry), c)

        return surf

    def _create_procedural_apparition(self, width: int, height: int) -> pygame.Surface:
        """Gera uma silhueta espectral sinistra para os sustos relâmpago no labirinto."""
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        cx, cy = width // 2, height // 2

        # Corpo esfumaçado
        body_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(body_surf, (20, 25, 35, 210), (cx - 90, cy - 140, 180, 280))
        pygame.draw.circle(body_surf, (30, 35, 45, 230), (cx, cy - 80), 55)

        # Olhos brancos brilhantes no escuro
        pygame.draw.circle(body_surf, (240, 250, 255, 255), (cx - 18, cy - 85), 7)
        pygame.draw.circle(body_surf, (240, 250, 255, 255), (cx + 18, cy - 85), 7)
        pygame.draw.circle(body_surf, (0, 200, 255, 180), (cx - 18, cy - 85), 12)
        pygame.draw.circle(body_surf, (0, 200, 255, 180), (cx + 18, cy - 85), 12)

        # Boca rasgada
        pygame.draw.arc(body_surf, (0, 0, 0, 240), (cx - 20, cy - 65, 40, 30), math.pi, 2 * math.pi, 4)

        surf.blit(body_surf, (0, 0))
        return surf

    def _create_procedural_wallpaper(self, width: int, height: int) -> pygame.Surface:
        """Papel de parede retrô sombrio com textura de ruído."""
        surf = pygame.Surface((width, height))
        surf.fill((0, 48, 48))  # Retro teal sombrio

        # Adiciona um padrão geométrico sutil dos anos 90
        for y in range(0, height, 40):
            for x in range(0, width, 40):
                pygame.draw.rect(surf, (0, 42, 42), (x, y, 38, 38), 1)

        return surf

    def _create_icon_folder(self, width: int = 48, height: int = 48) -> pygame.Surface:
        """Ícone de pasta amarela clássica do Windows 95/98."""
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        # Aba traseira
        pygame.draw.polygon(surf, (190, 160, 40), [(4, 14), (18, 14), (24, 20), (44, 20), (44, 40), (4, 40)])
        # Frente da pasta amarela
        pygame.draw.polygon(surf, (240, 205, 50), [(4, 20), (44, 20), (40, 42), (2, 42)])
        pygame.draw.polygon(surf, (255, 235, 100), [(6, 22), (42, 22), (38, 40), (4, 40)], 1)
        # Borda escura
        pygame.draw.polygon(surf, (70, 50, 10), [(4, 20), (44, 20), (40, 42), (2, 42)], 2)
        return surf

    def _create_icon_danger_folder(self, width: int = 48, height: int = 48) -> pygame.Surface:
        """Ícone de pasta perigosa corrompida avermelhada."""
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        # Aba traseira
        pygame.draw.polygon(surf, (140, 20, 20), [(4, 14), (18, 14), (24, 20), (44, 20), (44, 40), (4, 40)])
        # Frente vermelha sangue
        pygame.draw.polygon(surf, (190, 30, 30), [(4, 20), (44, 20), (40, 42), (2, 42)])
        # Marca de caveira ou exclamação preta
        pygame.draw.line(surf, (10, 0, 0), (22, 24), (22, 33), 3)
        pygame.draw.circle(surf, (10, 0, 0), (22, 37), 2)
        pygame.draw.polygon(surf, (60, 0, 0), [(4, 20), (44, 20), (40, 42), (2, 42)], 2)
        return surf

    def _create_icon_file(self, width: int = 48, height: int = 48) -> pygame.Surface:
        """Ícone de arquivo de texto com canto dobrado clássico."""
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        # Papel branco com borda cinza
        pts = [(8, 6), (32, 6), (40, 14), (40, 42), (8, 42)]
        pygame.draw.polygon(surf, (245, 245, 250), pts)
        pygame.draw.polygon(surf, (100, 110, 120), pts, 2)
        # Canto dobrado
        pygame.draw.polygon(surf, (180, 190, 200), [(32, 6), (40, 14), (32, 14)])
        # Linhas de texto
        for y in [18, 24, 30, 36]:
            pygame.draw.line(surf, (70, 80, 95), (14, y), (34, y), 2)
        return surf

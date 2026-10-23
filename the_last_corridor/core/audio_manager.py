"""
Sistema Profissional de Áudio de Terror de THE LAST CORRIDOR.
Gerencia áudio em camadas, canais com prioridade, reprodução de arquivos WAV/OGG/MP3,
síntese sonora procedural com NumPy e biblioteca com pré-visualização para o criador.
"""

import pygame
import sys
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import math
import random
import shutil

try:
    from core.config import get_app_base_dir
except ImportError:
    from the_last_corridor.core.config import get_app_base_dir


class AudioManager:
    # Canais de áudio dedicados
    CH_AMBIENT = 0
    CH_JUMPSCARE = 1
    CH_GLITCH = 2
    CH_COMPUTER = 3
    CH_INTERACTION = 4
    CH_FOOTSTEPS = 5
    CH_PREVIEW = 6

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            self.base_dir = get_app_base_dir()
        else:
            self.base_dir = Path(base_dir)

        self.audio_dir = self.base_dir / "assets" / "audio"
        self._ensure_directories()

        self.is_initialized = False
        self._init_mixer()

        # Cache de arquivos carregados
        self._sound_cache: Dict[str, pygame.mixer.Sound] = {}

        # Controles de volume por categoria
        self.master_volume: float = 1.0
        self.jumpscare_volume: float = 1.0
        self.footstep_volume: float = 1.0
        self.ambient_volume: float = 0.5
        self.glitch_volume: float = 0.7
        self.computer_volume: float = 0.8
        self.interaction_volume: float = 0.6
        self.ambient_enabled: bool = True
        self.audio_muted: bool = False
        self.mute_ambient_during_jumpscare: bool = True

        # Estado atual
        self.current_ambient_mode: str = "maze"  # "maze" ou "desktop"
        self._ambient_active: bool = False
        self._ambient_paused_by_scare: bool = False
        self._last_footstep_time: float = 0.0
        self._footstep_index: int = 0

        # Sons procedurais de fallback
        self._procedural_sounds: Dict[str, pygame.mixer.Sound] = {}
        if self.is_initialized:
            self._generate_procedural_sounds()

    def _ensure_directories(self):
        """Garante a existência das subpastas organizadas de áudio."""
        for sub in ["jumpscares", "glitches", "computer", "ambience", "interactions"]:
            (self.audio_dir / sub).mkdir(parents=True, exist_ok=True)

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            pygame.mixer.set_num_channels(12)
            self.is_initialized = True
        except Exception as e:
            print(f"[AudioManager] Aviso: Não foi possível inicializar mixer de áudio: {e}")
            self.is_initialized = False

    # --- Carregamento e Validação de Arquivos ---

    def load_sound(self, path_str: str, fallback_key: str = "scream") -> Optional[pygame.mixer.Sound]:
        """Carrega um arquivo de áudio do disco ou retorna o som procedural correspondente."""
        if not self.is_initialized:
            return None

        if path_str:
            p = Path(path_str)
            if not p.is_absolute():
                found_path = None
                subdirs = ["", "jumpscares", "glitches", "computer", "ambience", "interactions", "footsteps"]
                base_roots = [
                    self.audio_dir,
                    self.base_dir / "assets" / "audio",
                    self.base_dir / "_internal" / "assets" / "audio",
                    Path(sys.executable).parent / "assets" / "audio" if getattr(sys, "frozen", False) else None,
                    Path(sys.executable).parent / "_internal" / "assets" / "audio" if getattr(sys, "frozen", False) else None,
                ]
                
                for r in base_roots:
                    if not r or not r.exists():
                        continue
                    if (r / p).is_file():
                        found_path = r / p
                        break
                    for sub in subdirs:
                        candidate = r / sub / p.name if sub else r / p.name
                        if candidate.is_file():
                            found_path = candidate
                            break
                    if found_path:
                        break
                
                if found_path:
                    p = found_path
                else:
                    p = self.audio_dir / p

            if p.exists() and p.is_file():
                cache_key = str(p.resolve())
                if cache_key in self._sound_cache:
                    return self._sound_cache[cache_key]
                try:
                    snd = pygame.mixer.Sound(str(p))
                    self._sound_cache[cache_key] = snd
                    return snd
                except Exception as e:
                    print(f"[AudioManager] Falha ao decodificar áudio '{path_str}': {e}. Usando som de fallback.")

        return self._procedural_sounds.get(fallback_key)

    def validate_audio_file(self, path_str: str) -> Tuple[bool, str]:
        """Verifica se o arquivo de áudio existe e possui formato suportado (WAV, OGG, MP3)."""
        try:
            p = Path(path_str)
            if not p.exists() or not p.is_file():
                return False, "Arquivo não encontrado."
            ext = p.suffix.lower()
            if ext not in [".wav", ".ogg", ".mp3"]:
                return False, f"Formato '{ext}' não suportado (use WAV, OGG ou MP3)."
            pygame.mixer.Sound(str(p))
            return True, "Áudio válido e pronto para uso."
        except Exception as e:
            return False, f"Erro ao processar áudio: {e}"

    def list_audio_files(self, category: str = "") -> List[str]:
        """Retorna lista de caminhos relativos de arquivos de áudio encontrados na biblioteca."""
        if not self.audio_dir.exists():
            return []
        target_dir = self.audio_dir / category if category else self.audio_dir
        if not target_dir.exists():
            return []
        files = []
        for p in target_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in [".wav", ".ogg", ".mp3"]:
                rel = p.relative_to(self.audio_dir)
                files.append(str(rel).replace("\\", "/"))
        return sorted(files)

    def import_audio_file(self, source_path: str, category: str = "jumpscares") -> Tuple[bool, str]:
        """Copia um arquivo de áudio externo para a pasta apropriada de assets."""
        valid, msg = self.validate_audio_file(source_path)
        if not valid:
            return False, msg
        src = Path(source_path)
        dest_dir = self.audio_dir / category
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / src.name
        try:
            shutil.copy2(src, dest_file)
            rel_path = f"{category}/{src.name}"
            return True, rel_path
        except Exception as e:
            return False, f"Erro ao copiar arquivo: {e}"

    # --- Controles de Volume ---

    def set_volumes(
        self,
        master: float,
        jumpscare: float = 1.0,
        ambient: float = 0.5,
        glitch: float = 0.7,
        computer: float = 0.8,
        interaction: float = 0.6,
        footstep: float = 1.0,
        muted: bool = False
    ):
        self.master_volume = max(0.0, min(1.0, master))
        self.jumpscare_volume = max(0.0, min(1.0, jumpscare))
        self.ambient_volume = max(0.0, min(1.0, ambient))
        self.glitch_volume = max(0.0, min(1.0, glitch))
        self.computer_volume = max(0.0, min(1.0, computer))
        self.interaction_volume = max(0.0, min(1.0, interaction))
        self.footstep_volume = max(0.0, min(1.0, footstep))
        self.audio_muted = muted

        # Aplica volume ao canal ambiente ativo
        if self.is_initialized:
            ch_amb = pygame.mixer.Channel(self.CH_AMBIENT)
            if ch_amb.get_busy():
                vol = 0.0 if self.audio_muted else (self.master_volume * self.ambient_volume)
                ch_amb.set_volume(vol)

    def get_effective_volume(self, category_vol: float) -> float:
        if self.audio_muted:
            return 0.0
        return max(0.0, min(1.0, self.master_volume * category_vol))

    # --- Reprodução com Prioridade (A, B, C, D, E, F) ---

    def play_jumpscare(self, path_str: str = "", sound_type: str = "scream", volume_mult: float = 1.0):
        """
        Categoria A e C: Jumpscare principal e pastas perigosas.
        Possui a mais alta prioridade: interrompe o som ambiente e toca com impacto total.
        """
        if not self.is_initialized:
            return

        ch = pygame.mixer.Channel(self.CH_JUMPSCARE)
        # Previne sobreposição de sustos simultâneos
        if ch.get_busy():
            return

        # Pausa o som ambiente para dar sensação de choque e silêncio repentino
        if self.mute_ambient_during_jumpscare:
            ch_amb = pygame.mixer.Channel(self.CH_AMBIENT)
            if ch_amb.get_busy() or self._ambient_active:
                ch_amb.pause()
                self._ambient_paused_by_scare = True

        snd = self.load_sound(path_str, fallback_key=sound_type)
        if snd:
            vol = self.get_effective_volume(self.jumpscare_volume * volume_mult)
            snd.set_volume(vol)
            ch.play(snd)

    def play_apparition(self, path_str: str = "", sound_type: str = "glitch", probability: float = 0.8):
        """
        Categoria B: Imagens que piscam durante o labirinto.
        Suporta silêncio estocástico e efeitos curtos (glitch, static, whisper, pop, impact).
        Tenta carregar WAV de assets/audio/glitches/ antes de usar o procedural.
        """
        if not self.is_initialized or sound_type == "silent":
            return

        # Silêncio psicológico intencional em algumas aparições
        if random.random() > probability:
            return

        ch = pygame.mixer.Channel(self.CH_GLITCH)
        if ch.get_busy():
            return

        # Mapeamento para os arquivos WAV gerados
        _glitch_files = {
            "glitch":    "glitches/glitch_digital.wav",
            "static":    "glitches/glitch_static.wav",
            "pop":       "glitches/glitch_pop.wav",
            "distortion":"glitches/glitch_distort.wav",
        }
        effective_path = path_str or _glitch_files.get(sound_type, "")
        snd = self.load_sound(effective_path, fallback_key=sound_type)
        if snd:
            vol = self.get_effective_volume(self.glitch_volume)
            snd.set_volume(vol)
            ch.play(snd)

    def play_computer_sound(self, sound_name: str, path_str: str = ""):
        """
        Categoria D: Efeitos do computador antigo simulado (boot beep, degauss, drive seek).
        Tenta carregar do arquivo WAV em assets/audio/computer/ antes de usar o procedural.
        """
        if not self.is_initialized:
            return

        ch = pygame.mixer.Channel(self.CH_COMPUTER)
        # Mapeamento de nome para arquivo WAV gerado
        _computer_files = {
            "pc_boot_beep": "computer/boot_beep.wav",
            "crt_degauss":  "computer/degauss.wav",
            "drive_seek":   "computer/drive_seek.wav",
            "error_beep":   "computer/error_beep.wav",
            "hum":          "computer/hum.wav",
        }
        wav_path = path_str or _computer_files.get(sound_name, "")
        snd = self.load_sound(wav_path, fallback_key=sound_name)
        if snd:
            vol = self.get_effective_volume(self.computer_volume)
            snd.set_volume(vol)
            ch.play(snd)

    def play_ui_sound(self, sound_name: str):
        """
        Categoria F: Sons de interação (folder_open, window_close, doc_open, error, success, code_error, click).
        Tenta carregar do arquivo WAV em assets/audio/interactions/ antes de usar o procedural.
        """
        if not self.is_initialized:
            return

        ch = pygame.mixer.Channel(self.CH_INTERACTION)
        # Mapeamento de nome para arquivo WAV gerado
        _interaction_files = {
            "folder_open":  "interactions/folder_open.wav",
            "window_close": "interactions/window_close.wav",
            "doc_open":     "interactions/doc_open.wav",
            "error":        "interactions/error.wav",
            "success":      "interactions/success.wav",
            "code_error":   "interactions/code_error.wav",
        }
        wav_path = _interaction_files.get(sound_name, "")
        if wav_path:
            snd = self.load_sound(wav_path, fallback_key=sound_name)
        else:
            # Sons sem arquivo WAV (ex: "click") usam apenas o procedural
            snd = self._procedural_sounds.get(sound_name)
        if snd:
            vol = self.get_effective_volume(self.interaction_volume)
            snd.set_volume(vol)
            ch.play(snd)

    def play_footstep(self):
        """Passos nítidos e pesados no labirinto com alternância."""
        if not self.is_initialized or self.audio_muted:
            return
        
        import time
        now = time.time()
        # Controle de cadência mínima de 220ms
        if now - self._last_footstep_time < 0.22:
            return
        self._last_footstep_time = now

        ch = pygame.mixer.Channel(self.CH_FOOTSTEPS)

        # Usa passos.wav como arquivo de passos
        step_file = "footsteps/passos.wav"

        snd = self.load_sound(step_file, fallback_key="footstep")
        if snd:
            vol = self.get_effective_volume(self.footstep_volume)
            snd.set_volume(vol)
            ch.play(snd)

    def start_ambient_drone(self, mode: str = "maze"):
        """
        Categoria E: Sons ambientes contínuos (Labirinto ou Desktop Retrô).
        """
        if not self.is_initialized or not self.ambient_enabled:
            return

        self.current_ambient_mode = mode
        self._ambient_active = True
        self._ambient_paused_by_scare = False
        snd_key = "ambient_maze" if mode == "maze" else "ambient_desktop"
        snd = self._procedural_sounds.get(snd_key)

        ch = pygame.mixer.Channel(self.CH_AMBIENT)
        if snd:
            vol = self.get_effective_volume(self.ambient_volume)
            snd.set_volume(vol)
            ch.play(snd, loops=-1)

    def stop_ambient_drone(self):
        if self.is_initialized:
            pygame.mixer.Channel(self.CH_AMBIENT).stop()
            self._ambient_active = False
            self._ambient_paused_by_scare = False

    def resume_ambient(self):
        """Retoma o som ambiente após o término do susto."""
        if not self.is_initialized or not self.ambient_enabled:
            return

        ch = pygame.mixer.Channel(self.CH_AMBIENT)
        if self._ambient_paused_by_scare:
            if ch.get_busy():
                ch.unpause()
            else:
                self.start_ambient_drone(self.current_ambient_mode)
            self._ambient_paused_by_scare = False
        elif not ch.get_busy():
            self.start_ambient_drone(self.current_ambient_mode)

    # --- Pré-Visualização no Painel do Criador ---

    def start_preview(self, path_str: str = "", sound_type: str = "scream"):
        """Toca um efeito de áudio no canal de teste do painel do criador."""
        if not self.is_initialized:
            return
        ch = pygame.mixer.Channel(self.CH_PREVIEW)
        ch.stop()

        snd = self.load_sound(path_str, fallback_key=sound_type)
        if snd:
            vol = self.get_effective_volume(1.0)
            snd.set_volume(vol)
            ch.play(snd)

    def stop_preview(self):
        """Interrompe a pré-visualização de áudio."""
        if self.is_initialized:
            pygame.mixer.Channel(self.CH_PREVIEW).stop()

    def is_preview_playing(self) -> bool:
        if not self.is_initialized:
            return False
        return pygame.mixer.Channel(self.CH_PREVIEW).get_busy()

    # --- Síntese Sonora Procedural Completa com NumPy ---

    def _generate_procedural_sounds(self):
        sr = 44100

        # --- A & C: Jumpscares ---
        # 1. Scream (Grito agudo distorcido com impacto metálico)
        dur = 2.0
        t = np.linspace(0, dur, int(sr * dur), False)
        sub = np.sin(2 * np.pi * (55 * np.exp(-t * 3.5)) * t) * np.exp(-t * 2.0)
        # Voz estridente modulada
        screech = (
            np.sin(2 * np.pi * 880 * t) +
            np.sin(2 * np.pi * 932 * t) * 0.8 +
            np.sin(2 * np.pi * 1244 * t) * 0.6 +
            np.sin(2 * np.pi * (650 + 250 * np.sin(2 * np.pi * 14 * t)) * t) * 0.7
        )
        noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 1.8)
        scream_wave = (sub * 0.55 + screech * 0.35 + noise * 0.4) * np.exp(-t * 0.7)
        self._procedural_sounds["scream"] = self._create_sound(scream_wave, sr)

        # 2. Roar (Rugido monstruoso gutural profundo)
        dur_r = 2.4
        t_r = np.linspace(0, dur_r, int(sr * dur_r), False)
        # Modulação FM em frequências graves (120Hz descendo para 35Hz)
        carrier = np.sin(2 * np.pi * (110 * np.exp(-t_r * 0.8)) * t_r + 4.0 * np.sin(2 * np.pi * 45 * t_r))
        rumble = np.sin(2 * np.pi * 38 * t_r) * np.exp(-t_r * 0.5)
        growl_noise = (np.random.rand(len(t_r)) * 2 - 1) * 0.35 * np.exp(-t_r * 0.9)
        roar_wave = (carrier * 0.6 + rumble * 0.5 + growl_noise) * np.exp(-t_r * 0.6)
        self._procedural_sounds["roar"] = self._create_sound(roar_wave, sr)

        # 3. Impact Screech (Golpe sonoro grave + estilhaço metálico)
        dur_i = 1.6
        t_i = np.linspace(0, dur_i, int(sr * dur_i), False)
        slam = np.sin(2 * np.pi * (70 * np.exp(-t_i * 8.0)) * t_i) * np.exp(-t_i * 3.5)
        metal = np.sin(2 * np.pi * 1760 * t_i) * np.sin(2 * np.pi * 2340 * t_i) * np.exp(-t_i * 2.0)
        impact_wave = (slam * 0.7 + metal * 0.45 + (np.random.rand(len(t_i)) * 2 - 1) * 0.3 * np.exp(-t_i * 2.5))
        self._procedural_sounds["impact_screech"] = self._create_sound(impact_wave, sr)

        # 4. Distortion (Pulso estático violento de corte digital)
        dur_d = 1.2
        t_d = np.linspace(0, dur_d, int(sr * dur_d), False)
        buzz = np.sign(np.sin(2 * np.pi * 150 * t_d) + np.sin(2 * np.pi * 225 * t_d)) * 0.6
        dist_wave = buzz * np.exp(-t_d * 1.5)
        self._procedural_sounds["distortion"] = self._create_sound(dist_wave, sr)

        # --- B: Imagens que Piscam (Glitches do Labirinto) ---
        # 5. Glitch Digital Curto (75ms)
        dur_g = 0.08
        t_g = np.linspace(0, dur_g, int(sr * dur_g), False)
        glitch_wave = (np.random.rand(len(t_g)) * 2 - 1) * np.sin(2 * np.pi * 1400 * t_g)
        self._procedural_sounds["glitch"] = self._create_sound(glitch_wave, sr)

        # 6. Static (Estática analógica de TV antiga - 140ms)
        dur_s = 0.14
        t_s = np.linspace(0, dur_s, int(sr * dur_s), False)
        stat_noise = (np.random.rand(len(t_s)) * 2 - 1) * 0.5
        crt_tone = np.sin(2 * np.pi * 15625 * t_s) * 0.15  # 15.6 kHz frequência horizontal de CRT
        self._procedural_sounds["static"] = self._create_sound(stat_noise + crt_tone, sr)

        # 7. Whisper (Sussurro espectral)
        dur_w = 0.35
        t_w = np.linspace(0, dur_w, int(sr * dur_w), False)
        breath = (np.random.rand(len(t_w)) * 2 - 1) * np.sin(2 * np.pi * (600 + 300 * np.sin(2 * np.pi * 5 * t_w)) * t_w) * np.exp(-t_w * 4.0)
        self._procedural_sounds["whisper"] = self._create_sound(breath * 0.6, sr)

        # 8. Pop (Estalo elétrico súbito - 25ms)
        dur_p = 0.03
        t_p = np.linspace(0, dur_p, int(sr * dur_p), False)
        pop_wave = np.sin(2 * np.pi * 2800 * t_p) * np.exp(-t_p * 180)
        self._procedural_sounds["pop"] = self._create_sound(pop_wave, sr)

        # 9. Sub Impact (Impacto grave breve - 120ms)
        dur_sub = 0.15
        t_sub = np.linspace(0, dur_sub, int(sr * dur_sub), False)
        sub_wave = np.sin(2 * np.pi * (52 * np.exp(-t_sub * 6)) * t_sub) * np.exp(-t_sub * 12) * 0.8
        self._procedural_sounds["sub_impact"] = self._create_sound(sub_wave, sr)

        # --- D: Computador Antigo Simulado ---
        # 10. POST Beep (Bipe 820Hz da BIOS)
        dur_b = 0.22
        t_b = np.linspace(0, dur_b, int(sr * dur_b), False)
        beep_wave = np.sign(np.sin(2 * np.pi * 820 * t_b)) * 0.25 * np.exp(-t_b * 3.0)
        self._procedural_sounds["pc_boot_beep"] = self._create_sound(beep_wave, sr)

        # 11. CRT Degauss (Pancada magnética com zumbido harmônico dos tubos CRT)
        dur_deg = 0.85
        t_deg = np.linspace(0, dur_deg, int(sr * dur_deg), False)
        thud = np.sin(2 * np.pi * 45 * t_deg) * np.exp(-t_deg * 5.0) * 0.8
        buzz = (np.sin(2 * np.pi * 120 * t_deg) + np.sin(2 * np.pi * 240 * t_deg) * 0.5) * np.exp(-t_deg * 2.2) * 0.4
        self._procedural_sounds["crt_degauss"] = self._create_sound(thud + buzz, sr)

        # 12. Drive Seek (Ruído mecânico de cabeça de leitura de disco rígido IDE antigo)
        dur_dr = 0.35
        t_dr = np.linspace(0, dur_dr, int(sr * dur_dr), False)
        clicks = np.zeros(len(t_dr))
        # Gera série de cliques rápidos a cada poucos milissegundos
        for idx in range(0, len(t_dr), int(sr * 0.045)):
            if idx < len(clicks) - 200:
                clicks[idx:idx + 180] = (np.random.rand(180) * 2 - 1) * np.exp(-np.linspace(0, 1, 180) * 8.0)
        self._procedural_sounds["drive_seek"] = self._create_sound(clicks * 0.45, sr)

        # --- E: Sons Ambientes ---
        # 13. Ambient Maze (Zumbido escuro com pulsação binaural de 3Hz)
        dur_am = 6.0
        t_am = np.linspace(0, dur_am, int(sr * dur_am), False)
        drone1 = np.sin(2 * np.pi * 46 * t_am)
        drone2 = np.sin(2 * np.pi * 49 * t_am) * 0.7  # Batimento acústico de 3Hz
        drone3 = np.sin(2 * np.pi * 92 * t_am) * 0.3
        # Envelope suave de ponta para loop perfeito
        fade_len = int(sr * 0.2)
        env = np.ones(len(t_am))
        env[:fade_len] = np.linspace(0, 1, fade_len)
        env[-fade_len:] = np.linspace(1, 0, fade_len)
        self._procedural_sounds["ambient_maze"] = self._create_sound((drone1 + drone2 + drone3) * 0.3 * env, sr)

        # 14. Ambient Desktop (Zumbido elétrico suave de escritório/computador)
        dur_ad = 6.0
        t_ad = np.linspace(0, dur_ad, int(sr * dur_ad), False)
        hum60 = np.sin(2 * np.pi * 60 * t_ad) * 0.25
        hum120 = np.sin(2 * np.pi * 120 * t_ad) * 0.12
        crt_whine = np.sin(2 * np.pi * 15625 * t_ad) * 0.03
        self._procedural_sounds["ambient_desktop"] = self._create_sound((hum60 + hum120 + crt_whine) * env, sr)

        # --- F: Sons de Interação ---
        # 15. Footstep (Passo suave no piso escuro)
        dur_fs = 0.07
        t_fs = np.linspace(0, dur_fs, int(sr * dur_fs), False)
        fs_wave = np.sin(2 * np.pi * (75 * np.exp(-t_fs * 30)) * t_fs) * np.exp(-t_fs * 40) * 0.35
        self._procedural_sounds["footstep"] = self._create_sound(fs_wave, sr)

        # 16. Click / Window Open
        dur_cl = 0.03
        t_cl = np.linspace(0, dur_cl, int(sr * dur_cl), False)
        click_wave = (np.random.rand(len(t_cl)) * 2 - 1) * np.exp(-t_cl * 140) * 0.3
        self._procedural_sounds["click"] = self._create_sound(click_wave, sr)
        self._procedural_sounds["folder_open"] = self._create_sound(click_wave, sr)
        self._procedural_sounds["window_close"] = self._create_sound(click_wave * 0.8, sr)
        self._procedural_sounds["doc_open"] = self._create_sound(click_wave, sr)

        # 17. Error Beep (Erro retrô)
        dur_err = 0.22
        t_err = np.linspace(0, dur_err, int(sr * dur_err), False)
        err_wave = (np.sign(np.sin(2 * np.pi * 220 * t_err)) + np.sign(np.sin(2 * np.pi * 175 * t_err))) * 0.18 * np.exp(-t_err * 6)
        self._procedural_sounds["error"] = self._create_sound(err_wave, sr)
        self._procedural_sounds["code_error"] = self._create_sound(err_wave, sr)

        # 18. Success / Final Chime
        dur_suc = 2.0
        t_suc = np.linspace(0, dur_suc, int(sr * dur_suc), False)
        suc_wave = (
            np.sin(2 * np.pi * 440 * t_suc) * 0.3 +
            np.sin(2 * np.pi * 554.37 * t_suc) * 0.25 +
            np.sin(2 * np.pi * 659.25 * t_suc) * 0.25 +
            np.sin(2 * np.pi * 880 * t_suc) * 0.2
        ) * np.exp(-t_suc * 1.5)
        self._procedural_sounds["success"] = self._create_sound(suc_wave, sr)

    def _create_sound(self, wave: np.ndarray, sr: int) -> pygame.mixer.Sound:
        """Converte um vetor de áudio normalizado (-1.0 a 1.0) em pygame.mixer.Sound estéreo 16-bit."""
        wave = np.clip(wave, -1.0, 1.0)
        int16_wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.column_stack((int16_wave, int16_wave))
        return pygame.sndarray.make_sound(stereo_wave)

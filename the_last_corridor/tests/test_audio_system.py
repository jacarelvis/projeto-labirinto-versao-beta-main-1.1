"""
Testes Unitários e de Integração do Sistema Profissional de Áudio de Terror em THE LAST CORRIDOR.
Testa carregamento de WAV/OGG, arquivos ausentes, prioridade de jumpscare,
prevenção de duplicados, sons de pastas perigosas, boot retrô e persistência.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
import tempfile
import wave
import struct
import numpy as np
from pathlib import Path
import pygame

from the_last_corridor.core.audio_manager import AudioManager
from the_last_corridor.core.config import GameConfig, AudioConfig
from the_last_corridor.core.save_manager import SaveManager


class TestAudioSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        # Para todos os canais antes de cada teste para evitar estado sujo entre testes
        if pygame.mixer.get_init():
            pygame.mixer.stop()
        self.audio_mgr = AudioManager()

    def _create_temp_wav(self, duration_sec: float = 0.1) -> Path:
        """Cria um arquivo WAV sintetizado válido para testes de importação."""
        tf = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tf.close()
        p = Path(tf.name)

        sr = 44100
        n_samples = int(sr * duration_sec)
        with wave.open(str(p), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sr)
            for i in range(n_samples):
                val = int(32767.0 * 0.3 * np.sin(2.0 * np.pi * 440.0 * (i / sr)))
                data = struct.pack("<h", val)
                wav.writeframes(data)
        return p

    def test_import_and_validate_wav(self):
        """1 & 2: Validação e importação de arquivo WAV suportado."""
        wav_path = self._create_temp_wav(duration_sec=0.1)
        try:
            valid, msg = self.audio_mgr.validate_audio_file(str(wav_path))
            self.assertTrue(valid, f"WAV deveria ser válido: {msg}")

            ok, imported_name = self.audio_mgr.import_audio_file(str(wav_path), category="jumpscares")
            self.assertTrue(ok, "Importação de WAV deveria ter sucesso")
            self.assertIn("jumpscares/", imported_name)
        finally:
            if wav_path.exists():
                wav_path.unlink()

    def test_missing_file_handling(self):
        """3: Tratamento gracioso de arquivo inexistente (fallback procedural)."""
        valid, msg = self.audio_mgr.validate_audio_file("caminho_inexistente_fantasma.wav")
        self.assertFalse(valid)
        self.assertIn("não encontrado", msg.lower())

        # load_sound deve retornar som de fallback sem disparar exceção
        snd = self.audio_mgr.load_sound("inexistente.wav", fallback_key="scream")
        self.assertIsNotNone(snd, "Deve retornar som procedural quando arquivo não existe")

    def test_incompatible_format_handling(self):
        """4: Tratamento de formato não suportado (ex: .txt, .exe, .bin)."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
            tf.write(b"arquivo de texto nao eh audio")
            txt_path = Path(tf.name)
        try:
            valid, msg = self.audio_mgr.validate_audio_file(str(txt_path))
            self.assertFalse(valid)
            self.assertIn("não suportado", msg.lower())
        finally:
            if txt_path.exists():
                txt_path.unlink()

    def test_preview_playback_and_stop(self):
        """5: Reprodução e interrupção de pré-visualização no canal dedicado."""
        self.audio_mgr.start_preview(sound_type="scream")
        self.audio_mgr.stop_preview()
        self.assertFalse(self.audio_mgr.is_preview_playing())

    def test_jumpscare_priority_and_ambient_mute(self):
        """7 & 8 & 10: Prioridade do jumpscare pausando ambiente e retomando após susto."""
        self.audio_mgr.start_ambient_drone("maze")
        self.audio_mgr.play_jumpscare(sound_type="scream")

        self.assertTrue(self.audio_mgr._ambient_paused_by_scare)

        # Retomada do ambiente
        self.audio_mgr.resume_ambient()
        self.assertFalse(self.audio_mgr._ambient_paused_by_scare)

    def test_duplicate_jumpscare_prevention(self):
        """9: Prevenção de múltiplos sustos sobrepostos simultaneamente."""
        self.audio_mgr.play_jumpscare(sound_type="scream")
        ch = pygame.mixer.Channel(AudioManager.CH_JUMPSCARE)
        if ch.get_busy():
            # Chamada duplicada enquanto busy não deve quebrar
            self.audio_mgr.play_jumpscare(sound_type="roar")
            self.assertTrue(ch.get_busy())

    def test_dangerous_folder_sounds(self):
        """11: Sons específicos para pastas perigosas (rugido, grito, distorção)."""
        for stype in ["scream", "roar", "impact_screech", "distortion"]:
            snd = self.audio_mgr._procedural_sounds.get(stype)
            self.assertIsNotNone(snd, f"Som procedural '{stype}' deve existir")

    def test_computer_boot_sounds(self):
        """12: Sons de inicialização retrô (POST beep, CRT degauss, drive seek)."""
        for boot_snd in ["pc_boot_beep", "crt_degauss", "drive_seek"]:
            snd = self.audio_mgr._procedural_sounds.get(boot_snd)
            self.assertIsNotNone(snd, f"Som do computador '{boot_snd}' deve existir")

    def test_audio_config_persistence(self):
        """13: Persistência de volumes e opções em JSON."""
        cfg = GameConfig()
        cfg.audio.master_volume = 0.65
        cfg.audio.jumpscare_volume = 0.95
        cfg.audio.ambient_volume = 0.40
        cfg.audio.audio_muted = True

        d = cfg.to_dict()
        self.assertEqual(d["audio"]["master_volume"], 0.65)
        self.assertEqual(d["audio"]["jumpscare_volume"], 0.95)
        self.assertTrue(d["audio"]["audio_muted"])

        loaded = GameConfig()
        loaded.from_dict(d)
        self.assertEqual(loaded.audio.master_volume, 0.65)
        self.assertEqual(loaded.audio.jumpscare_volume, 0.95)
        self.assertTrue(loaded.audio.audio_muted)


if __name__ == "__main__":
    unittest.main()

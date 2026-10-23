"""
Gerenciador de Salvamento e Perfis do THE LAST CORRIDOR.
Gerencia persistência de perfis de usuário e estado salvo de partida para a opção CONTINUAR.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from .config import GameConfig, get_app_base_dir


class SaveManager:
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            self.base_dir = get_app_base_dir()
        else:
            self.base_dir = Path(base_dir)

        self.profiles_dir = self.base_dir / "assets" / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

        self.save_game_file = self.profiles_dir / "save_game.json"
        self.default_profile_file = self.profiles_dir / "default.json"

    def get_or_create_default_config(self) -> GameConfig:
        """Obtém ou cria a configuração padrão persistida."""
        if self.default_profile_file.exists():
            return GameConfig.load_from_file(self.default_profile_file)
        else:
            cfg = GameConfig()
            cfg.save_to_file(self.default_profile_file)
            return cfg

    def save_profile(self, name: str, config: GameConfig) -> Path:
        """Salva um perfil com o nome fornecido."""
        safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip()
        if not safe_name:
            safe_name = "perfil_custom"
        target_path = self.profiles_dir / f"{safe_name}.json"
        config.save_to_file(target_path)
        return target_path

    def load_profile(self, name: str) -> Optional[GameConfig]:
        """Carrega um perfil pelo nome."""
        safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip()
        target_path = self.profiles_dir / f"{safe_name}.json"
        if target_path.exists():
            return GameConfig.load_from_file(target_path)
        return None

    def list_profiles(self) -> list:
        """Retorna uma lista de nomes de perfis salvos."""
        return [f.stem for f in self.profiles_dir.glob("*.json") if f.name != "save_game.json"]

    def save_game_state(self, state_data: Dict[str, Any]):
        """Salva o progresso da partida atual para permitir a opção CONTINUAR."""
        try:
            with open(self.save_game_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=4)
        except Exception as e:
            print(f"[SaveManager] Falha ao salvar partida: {e}")

    def load_game_state(self) -> Optional[Dict[str, Any]]:
        """Carrega o progresso salvo da partida, se existir."""
        if not self.save_game_file.exists():
            return None
        try:
            with open(self.save_game_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[SaveManager] Falha ao carregar partida salva: {e}")
            return None

    def clear_game_state(self):
        """Limpa o save game atual ao vencer ou reiniciar."""
        if self.save_game_file.exists():
            try:
                self.save_game_file.unlink()
            except Exception as e:
                print(f"[SaveManager] Erro ao remover save temporário: {e}")

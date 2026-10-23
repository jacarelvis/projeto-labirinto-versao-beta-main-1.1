"""
Configurações Globais e Esquema de Dados do Projeto THE LAST CORRIDOR.
Gerencia opções de jogo, labirinto, aparições, jumpscares, sistema virtual e perfis JSON.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
import json
import sys
from pathlib import Path


def get_app_base_dir() -> Path:
    """Retorna o diretório base da aplicação (funciona em desenvolvimento e empacotado).

    Quando empacotado pelo PyInstaller, os assets ficam dentro de _internal/
    (sys._MEIPASS), não junto ao .exe. O diretório de saves/perfis fica junto
    ao .exe para ser gravável pelo usuário.
    """
    if getattr(sys, "frozen", False):
        # sys._MEIPASS aponta para _internal/, onde os assets ficam
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


@dataclass
class DisplayConfig:
    width: int = 1024
    height: int = 768
    fps: int = 60
    fullscreen: bool = False
    reduce_flashes: bool = False
    reduce_shakes: bool = False
    disable_intense_effects: bool = False
    crt_scanlines: bool = True


@dataclass
class AudioConfig:
    master_volume: float = 1.0
    jumpscare_volume: float = 1.0
    footstep_volume: float = 1.0
    ambient_volume: float = 0.5
    glitch_volume: float = 0.7
    computer_volume: float = 0.8
    interaction_volume: float = 0.6
    ambient_enabled: bool = True
    boot_sound_enabled: bool = True
    audio_muted: bool = False
    mute_ambient_during_jumpscare: bool = True


@dataclass
class MazeConfig:
    cols: int = 19
    rows: int = 19
    cell_size: int = 40
    player_speed: float = 4.0
    flashlight_radius: int = 135
    exit_x: int = 17
    exit_y: int = 17
    start_x: int = 1
    start_y: int = 1


@dataclass
class ApparitionItem:
    id: str = "apparition_default"
    image_path: str = "assets/images/aparicao_labirinto.png"
    sound_path: str = ""
    sound_type: str = "glitch"  # "glitch", "static", "whisper", "pop", "impact", "silent"
    sound_probability: float = 0.80  # 80% toca som, 20% susto em silêncio absoluto
    duration_ms: int = 180
    probability: float = 0.35
    min_interval_sec: float = 8.0
    min_distance_steps: int = 12
    intensity: float = 1.0
    position_mode: str = "center"  # "center" or "fullscreen"
    region_tag: str = "all"  # "all", "start", "mid", "near_exit"
    max_occurrences: int = -1  # -1 = ilimitado


@dataclass
class FinalJumpscareConfig:
    image_path: str = "assets/images/jumpscare_principal.png"
    sound_path: str = "assets/audio/jumpscares/grito.mp3"
    sound_type: str = "scream"  # "scream", "roar", "impact_screech", "distortion"
    sound_delay_ms: int = 0
    mute_ambient: bool = True
    volume: float = 1.0
    duration_ms: int = 4500
    screen_shake: bool = True
    visual_distortion: bool = True
    flash: bool = True
    zoom: bool = True


@dataclass
class DangerousFolderConfig:
    folder_path: str
    status: str = "dangerous"  # "safe", "suspicious", "dangerous"
    scare_image: str = "assets/images/jumpscare_pasta.png"
    scare_audio: str = "assets/audio/jumpscares/grito.mp3"
    sound_type: str = "scream"  # "scream", "roar", "whisper_glitch", "impact_static", "distortion"
    duration_ms: int = 3500
    volume: float = 1.0
    shake: bool = True
    trigger_once: bool = False
    has_triggered: bool = False
    return_to_parent: bool = True
    suspicious_message: str = "AVISO: Distorção magnética detectada nesta pasta."


@dataclass
class DesktopConfig:
    computer_name: str = "ARCHIVE-09"
    wallpaper_color: str = "#004040"  # Retro teal
    wallpaper_image: str = ""
    boot_duration_ms: int = 3200
    boot_lines: List[str] = field(default_factory=lambda: [
        "ARCHIVE-09 BIOS v3.20 (C) 1998 RETRO SYSTEMS CORP.",
        "CPU: 133 MHz CLOCK DETECTED. 32MB RAM INSTALLED... OK",
        "PRIMARY MASTER: 1.2 GB HARD DISK... INITIALIZED",
        "MOUNTING RECOVERY VIRTUAL FILE SYSTEM...",
        "WARNING: MEMORY LEAK DETECTED AT SEGMENT 0x00FF8C",
        "ERROR CODE 0x666: CORRUPTED RECORD RESTORED.",
        "RESUMING SUSPENDED SESSION...",
        "STARTING VIRTUAL DESKTOP INTERFACE..."
    ])


@dataclass
class InvestigationConfig:
    mandatory_message: str = "EXISTE UM ARQUIVO NO SEU COMPUTADOR, O ENCONTRE E ESCREVA O CODIGO AQUI"
    target_document_path: str = "Arquivos/sistema/acesso_restrito.txt"
    secret_code: str = "Venlafaxina"
    case_sensitive: bool = False
    strip_whitespace: bool = True
    victory_message: str = (
        "ARQUIVO RECONHECIDO. CODIGO ACEITO.\n\n"
        "A CONEXAO COM O TERMINAL FOI ENCERRADA COM SUCESSO.\n"
        "VOCE COMPREENDEU O QUE ACONTECEU NO ULTIMO CORREDOR."
    )


class GameConfig:
    def __init__(self):
        self.display = DisplayConfig()
        self.audio = AudioConfig()
        self.maze = MazeConfig()
        self.apparitions: List[ApparitionItem] = [
            ApparitionItem(
                id="default_shadow",
                image_path="assets/images/aparicao_labirinto.png",
                sound_path="",
                sound_type="glitch",
                sound_probability=0.80,
                duration_ms=180,
                probability=0.35,
                min_interval_sec=8.0,
                min_distance_steps=10
            )
        ]
        self.final_jumpscare = FinalJumpscareConfig(
            image_path="assets/images/jumpscare_principal.png",
            sound_type="scream"
        )
        self.desktop = DesktopConfig()
        self.investigation = InvestigationConfig()
        self.dangerous_folders: Dict[str, DangerousFolderConfig] = {
            "Meus Documentos/Pessoal/nao_abra": DangerousFolderConfig(
                folder_path="Meus Documentos/Pessoal/nao_abra",
                status="dangerous",
                scare_image="assets/images/jumpscare_pasta.png",
                sound_type="scream",
                duration_ms=2000,
                shake=True,
                trigger_once=False,
                return_to_parent=True
            ),
            "Lixeira": DangerousFolderConfig(
                folder_path="Lixeira",
                status="suspicious",
                suspicious_message="A Lixeira contem arquivos fragmentados corrompidos."
            )
        }
        self.filesystem_tree = self.get_default_filesystem_tree()

    @staticmethod
    def get_default_filesystem_tree() -> Dict[str, Any]:
        """Estrutura padrão do sistema de arquivos fictício."""
        return {
            "name": "root",
            "type": "folder",
            "children": {
                "Desktop": {
                    "type": "folder",
                    "children": {
                        "LEIA-ME.txt": {
                            "type": "file",
                            "content": (
                                "SE VOCE ESTA LENDO ISTO, O SISTEMA RECONHECEU SUA PRESENCA.\n"
                                "NAO DEVERIAM HAVER OUTRAS TESTEMUNHAS.\n\n"
                                "PROCURE NOS ARQUIVOS DO SISTEMA. O CODIGO ESTA ESCONDIDO ONDE\n"
                                "NINGUEM TEM AUTORIZACAO PARA MEXER."
                            )
                        },
                        "notas_antigas.txt": {
                            "type": "file",
                            "content": (
                                "Diario de manutencao:\n"
                                "- Os corredores estao mudando de lugar durante a noite.\n"
                                "- Trancamos o relatorio final e o codigo de contingencia em 'Arquivos/sistema'.\n"
                                "- Tome cuidado com pastas pessoais. Algo esta preso la dentro."
                            )
                        }
                    }
                },
                "Meus Documentos": {
                    "type": "folder",
                    "children": {
                        "Relatorios": {
                            "type": "folder",
                            "children": {
                                "relatorio_01.txt": {
                                    "type": "file",
                                    "content": (
                                        "RELATORIO 01 - PROJETO ULTIMO CORREDOR\n"
                                        "Data: 14/10/1998\n"
                                        "As cobaias relataram visoes de rostos desfigurados nas curvas.\n"
                                        "A sensacao de ser perseguido persiste mesmo apos o desligamento."
                                    )
                                },
                                "relatorio_final.txt": {
                                    "type": "file",
                                    "content": (
                                        "RELATORIO FINAL:\n"
                                        "Evacuacao imediata decretada.\n"
                                        "Para finalizar a simulacao, use a chave mestra gravada no arquivo de acesso restrito."
                                    )
                                }
                            }
                        },
                        "Pessoal": {
                            "type": "folder",
                            "children": {
                                "diario.txt": {
                                    "type": "file",
                                    "content": (
                                        "Hoje ouvi passos atras da porta do escritorio.\n"
                                        "Quando olhei, a luz do monitor oscilou.\n"
                                        "Se precisar do codigo, va em 'Arquivos/sistema'."
                                    )
                                },
                                "nao_abra": {
                                    "type": "folder",
                                    "children": {
                                        "aviso.txt": {
                                            "type": "file",
                                            "content": "VOCE NAO DEVERIA TER ENTRADO AQUI."
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "Arquivos": {
                    "type": "folder",
                    "children": {
                        "backup": {
                            "type": "folder",
                            "children": {
                                "registro.txt": {
                                    "type": "file",
                                    "content": "Backup corrompido em 31/10/1998."
                                }
                            }
                        },
                        "sistema": {
                            "type": "folder",
                            "children": {
                                "acesso_restrito.txt": {
                                    "type": "file",
                                    "content": (
                                        "=========================================\n"
                                        "ARQUIVO DE SEGURANCA NIVEL 5 - AUTORIZADO\n"
                                        "=========================================\n\n"
                                        "CODIGO DE CONTINGENCIA FINAL:\n\n"
                                        "        Venlafaxina\n\n"
                                        "DIGITE ESTE CODIGO NA JANELA DE VERIFICACAO\n"
                                        "PARA ENCERRAR O PROTOCOLO.\n"
                                        "========================================="
                                    )
                                }
                            }
                        }
                    }
                },
                "Lixeira": {
                    "type": "folder",
                    "children": {
                        "fragmentos.txt": {
                            "type": "file",
                            "content": "...nao olhe para tras... a saida nunca foi uma saida..."
                        }
                    }
                }
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """Converte a configuração em um dicionário serializável em JSON."""
        return {
            "display": asdict(self.display),
            "audio": asdict(self.audio),
            "maze": asdict(self.maze),
            "apparitions": [asdict(a) for a in self.apparitions],
            "final_jumpscare": asdict(self.final_jumpscare),
            "desktop": asdict(self.desktop),
            "investigation": asdict(self.investigation),
            "dangerous_folders": {k: asdict(v) for k, v in self.dangerous_folders.items()},
            "filesystem_tree": self.filesystem_tree
        }

    def from_dict(self, data: Dict[str, Any]):
        """Carrega a configuração a partir de um dicionário."""
        if "display" in data:
            self.display = DisplayConfig(**data["display"])
        if "audio" in data:
            self.audio = AudioConfig(**data["audio"])
        if "maze" in data:
            self.maze = MazeConfig(**data["maze"])
        if "apparitions" in data:
            self.apparitions = [ApparitionItem(**a) for a in data["apparitions"]]
        if "final_jumpscare" in data:
            self.final_jumpscare = FinalJumpscareConfig(**data["final_jumpscare"])
        if "desktop" in data:
            self.desktop = DesktopConfig(**data["desktop"])
        if "investigation" in data:
            self.investigation = InvestigationConfig(**data["investigation"])
        if "dangerous_folders" in data:
            self.dangerous_folders = {k: DangerousFolderConfig(**v) for k, v in data["dangerous_folders"].items()}
        if "filesystem_tree" in data:
            self.filesystem_tree = data["filesystem_tree"]

    def save_to_file(self, file_path: Path):
        """Salva a configuração em formato JSON formatado."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "GameConfig":
        """Carrega uma configuração de arquivo JSON com fallback automático."""
        cfg = cls()
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cfg.from_dict(data)
            except Exception as e:
                print(f"[Config] Erro ao carregar perfil '{file_path}': {e}. Usando configuração padrão.")
        return cfg

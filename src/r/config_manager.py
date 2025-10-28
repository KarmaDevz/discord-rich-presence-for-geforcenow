import tkinter as tk
from tkinter import filedialog
import logging
from pathlib import Path
from typing import Dict, Optional
from utils import safe_json_load
from constants import CONFIG_DIR

logger = logging.getLogger('geforce_presence')


class ConfigManager:
    def __init__(self, config_path_file: Path):
        self.config_path_file = Path(config_path_file)
        self.games_config: Dict = {}
        self.games_config_path: Optional[Path] = None
        self._load()

    def _load(self):
        if self.config_path_file.exists():
            try:
                p = Path(self.config_path_file.read_text(encoding="utf-8").strip())
                if p.exists():
                    j = safe_json_load(p)
                    if isinstance(j, dict):
                        self.games_config = j
                        self.games_config_path = p
                        logger.info(f"✅ Configuración cargada desde: {p}")
                        self._log_games_summary(verbose=True)
                        return
                    else:
                        logger.warning("⚠️ El archivo games_config no contiene un objeto JSON.")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo leer config_path_file: {e}")

        try:
            root = tk.Tk()
            root.withdraw()
            logger.info("📁 Selecciona tu archivo games_config.json (dialog)...")
            initialdir = str(CONFIG_DIR) if CONFIG_DIR.exists() else str(Path.home())
            initialfile = "games_config.json"

            suggested = Path(initialdir) / initialfile
            if suggested.exists():
                p = suggested
                self.games_config_path = p
                self.games_config = safe_json_load(p) or {}
                try:
                    self.config_path_file.write_text(str(p), encoding="utf-8")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo escribir config_path_file: {e}")
                logger.info(f"✅ Configuración guardada: {self.config_path_file}")
                self._log_games_summary()
                return

            p_str = filedialog.askopenfilename(
                title="Selecciona el archivo games_config_merged.json",
                filetypes=[("JSON Files", "*.json")],
                initialdir=CONFIG_DIR,
                initialfile="games_config_merged.json"
            )
            if not p_str:
                logger.error("❌ No se seleccionó ningún archivo.")
                return
            p = Path(p_str)
            self.games_config_path = p
            self.games_config = safe_json_load(p) or {}
            try:
                self.config_path_file.write_text(str(p), encoding="utf-8")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo escribir config_path_file: {e}")
            logger.info(f"✅ Configuración guardada: {self.config_path_file}")
            self._log_games_summary()
        except Exception as e:
            logger.error(f"❌ No se pudo abrir diálogo para seleccionar config: {e}")

    def _log_games_summary(self, verbose=False):
        count = len(self.games_config)
        if count == 0:
            logger.warning("⚠️ No se encontraron juegos en la configuración.")
            return
        logger.info(f"📦 Juegos cargados: {count}")

    def get_game_mapping(self):
        return self.games_config

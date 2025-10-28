import subprocess
from pathlib import Path
import psutil
import logging
from typing import Optional
import os
logger = logging.getLogger('geforce_presence')


class AppLauncher:
    @staticmethod
    def find_geforce_now() -> Optional[str]:
        possible = [
            Path(os.getenv("LOCALAPPDATA", "")) / "NVIDIA Corporation" / "GeForceNOW" / "CEF" / "GeForceNOW.exe"
        ]
        for p in possible:
            if p.exists():
                return str(p)
        return None

    @staticmethod
    def _is_process_running_by_name(target_name: str) -> bool:
        try:
            for proc in psutil.process_iter(attrs=['name']):
                name = (proc.info.get('name') or "").lower()
                if name == target_name.lower() or target_name.lower() in name:
                    return True
        except Exception:
            pass
        return False

    @staticmethod
    def launch_geforce_now():
        if AppLauncher._is_process_running_by_name("GeForceNOW.exe"):
            logger.info("💡 GeForce NOW ya está en ejecución")
            return
        path = AppLauncher.find_geforce_now()
        if path:
            logger.info("🚀 Iniciando GeForce NOW...")
            subprocess.Popen([path])
        else:
            from utils import save_cookie_to_env
            # show_message must be provided by caller; handle elsewhere
            logger.warning("GeForce NOW no encontrado en la ruta por defecto.")

    @staticmethod
    def find_discord() -> Optional[str]:
        p = Path(os.getenv("LOCALAPPDATA", "")) / "Discord" / "Update.exe"
        if p.exists():
            return str(p)
        return None

    @staticmethod
    def launch_discord():
        for proc in psutil.process_iter(attrs=['name']):
            name = (proc.info.get('name') or "").lower()
            if "discord" in name and "update" not in name:
                logger.info("💡 Discord ya está en ejecución")
                return
        updater = AppLauncher.find_discord()
        if updater:
            logger.info("🚀 Iniciando Discord...")
            subprocess.Popen([updater, "--processStart", "Discord.exe"])
        else:
            logger.warning("⚠️ No se encontró Discord instalado en la ruta por defecto.")

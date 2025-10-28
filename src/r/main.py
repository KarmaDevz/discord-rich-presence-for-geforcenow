# Project: geforce_presence_modular
# Structure: multiple python modules concatenated in this single canvas file for review.

#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

# Prepare directories and logging
from constants import *
from utils import safe_json_load
from config_manager import ConfigManager
from cookie_manager import CookieManager
from presence_manager import PresenceManager
from tray_icon import start_tray_icon, stop_tray_icon
from app_launcher import AppLauncher


CONFIG_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
LANG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger('geforce_presence')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

fh = RotatingFileHandler(str(LOG_FILE), maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(formatter)
logger.addHandler(sh)

try:
    load_dotenv(ENV_PATH)
    logger.debug(".env cargado")
except Exception:
    logger.debug("python-dotenv no disponible o .env no encontrado; usando variables de entorno del sistema")


def ensure_env_file(path: Path):
    try:
        if not path.exists():
            path.write_text(DEFAULT_ENV_CONTENT, encoding="utf-8")
            logger.info(f"✅ .env creado en: {path}")
    except PermissionError:
        appdata = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        appdir = appdata / "geforce_presence"
        appdir.mkdir(parents=True, exist_ok=True)
        alt = appdir / ".env"
        if not alt.exists():
            alt.write_text(DEFAULT_ENV_CONTENT, encoding="utf-8")
            logger.info(f"⚠️ No se pudo crear .env junto al exe; creado en: {alt}")

ensure_env_file(ENV_PATH)


# Acquire lock implementation kept in main for simplicity
import psutil, atexit, os

def acquire_lock():
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            if psutil.pid_exists(pid):
                logger.info(f"Ya existe otra instancia (PID {pid})")
                return False
            else:
                LOCK_FILE.unlink()
                logger.debug("Lock huérfano eliminado.")
        except Exception:
            try:
                LOCK_FILE.unlink()
            except Exception:
                pass
    LOCK_FILE.write_text(str(os.getpid()))
    atexit.register(release_lock)
    return True

def release_lock():
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass


def main():
    if not acquire_lock():
        print("Otra instancia ya está en ejecución")
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-launch-geforce", action="store_true")
    parser.add_argument("--no-launch-discord", action="store_true")
    parser.add_argument("--verbose", action="store_true", help="Mostrar lista completa de juegos en carga")
    parser.add_argument("--no-keepalive", action="store_true", help="Desactivar keep-alive (si está activado)")
    parser.add_argument("--tray", action="store_true", help="Forzar uso de icono en bandeja (si está disponible)")
    args = parser.parse_args()

    cfgm = ConfigManager(CONFIG_DIR / "config_path.txt")
    games = cfgm.get_game_mapping()

    if not args.no_launch_discord:
        AppLauncher.launch_discord()
    if not args.no_launch_geforce:
        AppLauncher.launch_geforce_now()

    # Prepare driver service for selenium
    from selenium.webdriver.edge.service import Service as EdgeService
    from utils import save_json
    driver_exec = str((Path(driver_path)))
    service = EdgeService(executable_path=driver_exec)

    cookie_mgr = CookieManager(env_cookie=None, test_url="")
    presence = PresenceManager(client_id=None, games_map=games, cookie_manager=cookie_mgr,
                               test_rich_url="", update_interval=10,
                               keep_alive=(not args.no_keepalive), service=service,
                               assets_dir=ASSETS_DIR, config_path_file=CONFIG_DIR / "config_path.txt")

    tray_started = False
    try:
        tray_started = start_tray_icon(ASSETS_DIR, on_quit_callback=lambda: presence.close(), presence_instance=presence, cookie_manager=cookie_mgr)
    except Exception as e:
        logger.debug(f"No se pudo iniciar tray: {e}")

    if not tray_started:
        logger.error("❌ No se pudo iniciar el tray. Instala pystray y Pillow.")
        sys.exit(1)

    try:
        presence.run_loop()
    finally:
        stop_tray_icon()
        presence.close()

if __name__ == "__main__":
    main()

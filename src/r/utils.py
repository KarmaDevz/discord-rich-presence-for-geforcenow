import json
import logging
from pathlib import Path
from typing import Optional, Dict
from dotenv import set_key

logger = logging.getLogger('geforce_presence')


def safe_json_load(path: Path) -> Optional[Dict]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error cargando JSON {path}: {e}")
        return None


def save_json(obj, path: Path):
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(obj, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error guardando JSON {path}: {e}")


def save_cookie_to_env(env_path: Path, cookie_value: str):
    try:
        if env_path.exists():
            set_key(str(env_path), "STEAM_COOKIE", cookie_value)
            logger.info("💾 Cookie guardada en .env correctamente.")
        else:
            logger.warning("⚠️ No se encontró el archivo .env para guardar la cookie.")
    except Exception as e:
        logger.error(f"❌ Error guardando cookie en .env: {e}")

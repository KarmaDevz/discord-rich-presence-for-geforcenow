#!/usr/bin/env python3
import argparse
import atexit
import json
import logging
import os
import shutil
import re
import signal
import sys
import tempfile
import subprocess
import threading
import time
import stat
import socket
from pathlib import Path

import psutil
import requests
import browser_cookie3
from dotenv import set_key
from logging.handlers import RotatingFileHandler
from typing import Dict, Optional
from bs4 import BeautifulSoup
from pypresence import Presence
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service as EdgeService


def resource_path(*parts):
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        base = Path(__file__).resolve().parent.parent
    return base.joinpath(*parts)

BASE_DIR = resource_path("")      
CONFIG_DIR = resource_path("config")
LOGS_DIR = resource_path("logs")
ASSETS_DIR = resource_path("assets")
driver_path = resource_path("tools", "msedgedriver.exe")
LOG_FILE = LOGS_DIR / "geforce_presence.log"
ENV_PATH = resource_path(".env")

DEFAULT_ENV_CONTENT = """CLIENT_ID = '1095416975028650046'
UPDATE_INTERVAL = 10
CONFIG_PATH_FILE = ''
TEST_RICH_URL = 'https://steamcommunity.com/dev/testrichpresence'
STEAM_COOKIE=''
"""


CONFIG_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

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

logger.debug(f"Base directory: {BASE_DIR}")
logger.debug(f"Config directory: {CONFIG_DIR}")
logger.debug(f"Logs directory: {LOGS_DIR}")

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
        global ENV_PATH
        ENV_PATH = alt
ensure_env_file(ENV_PATH)

try:
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)
    logger.debug(".env cargado")
except Exception:
    logger.debug("python-dotenv no disponible o .env no encontrado; usando variables de entorno del sistema")


def ensure_driver_executable(src_path: Path) -> str:
    try:
        if not src_path.exists():
            logger.warning(f"msedgedriver no encontrado en recursos: {src_path}")
            return str(src_path) 
        tmpdir = Path(tempfile.gettempdir()) / "geforce_driver"
        tmpdir.mkdir(parents=True, exist_ok=True)
        dest = tmpdir / src_path.name
        shutil.copy2(str(src_path), str(dest))
        try:
            dest.chmod(dest.stat().st_mode | stat.S_IEXEC)
        except Exception:
            pass
        return str(dest)
    except Exception as e:
        logger.error(f"Error preparando msedgedriver: {e}")
        return str(src_path)
    
driver_exec = ensure_driver_executable(Path(driver_path))
service = EdgeService(executable_path=str(driver_exec))
TEST_RICH_URL = os.getenv("TEST_RICH_URL", "").strip()
CLIENT_ID = os.getenv("CLIENT_ID", "").strip() or None
STEAM_COOKIE_ENV = os.getenv("STEAM_COOKIE", "").strip() or None

CONFIG_PATH_FILE = CONFIG_DIR / "config_path.txt"

UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "10"))

def safe_json_load(path: Path) -> Optional[Dict]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error cargando JSON {path}: {e}")
        return None
    
def save_cookie_to_env(cookie_value: str):
    try:
        if ENV_PATH.exists():
            set_key(str(ENV_PATH), "STEAM_COOKIE", cookie_value)
            logger.info("💾 Cookie guardada en .env correctamente.")
        else:
            logger.warning("⚠️ No se encontró el archivo .env para guardar la cookie.")
    except Exception as e:
        logger.error(f"❌ Error guardando cookie en .env: {e}")

def save_json(obj, path: Path):
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(obj, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error guardando JSON {path}: {e}")

class AppMonitor:
    @staticmethod
    def is_process_running(name: str) -> bool:
        for proc in psutil.process_iter(attrs=['name']):
            if name.lower() in (proc.info['name'] or "").lower():
                return True
        return False

    @staticmethod
    def kill_process(name: str):
        for proc in psutil.process_iter(attrs=['name']):
            if name.lower() in (proc.info['name'] or "").lower():
                try:
                    proc.kill()
                    logger.info(f"💀 Proceso {name} cerrado.")
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    logger.error(f"⚠️ No se pudo cerrar {name}: {e}")

    @staticmethod
    def monitor_geforce_and_dumb():
        if not AppMonitor.is_process_running("GeForceNOW.exe"):
            AppMonitor.kill_process("dumb.exe")

    @staticmethod
    def launch_dumb(path_dumb: str):
        AppMonitor.kill_process("dumb.exe")
        subprocess.Popen([path_dumb])
        logger.info("🚀 dumb.exe iniciado.")

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
                        logger.info(f"ruta de configuración: {self.config_path_file}")
                        self._log_games_summary(verbose=True)
                        return
                    else:
                        logger.warning("⚠️ El archivo games_config no contiene un objeto JSON.")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo leer config_path_file: {e}")

        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            logger.info("📁 Selecciona tu archivo games_config.json (dialog)...")
            p_str = filedialog.askopenfilename(
                title="Selecciona el archivo games_config.json",
                filetypes=[("JSON Files", "*.json")]
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

class CookieManager:
    def __init__(self, env_cookie: Optional[str] = None, test_url: str = TEST_RICH_URL):
        self.env_cookie = env_cookie
        self.test_url = test_url

    def validar_cookie(self, cookie_value: str) -> bool:
        try:
            s = requests.Session()
            s.cookies.set('steamLoginSecure', cookie_value)
            r = s.get(self.test_url, timeout=10)
            if r.status_code == 200 and "Sign In" not in r.text and "login" not in r.url.lower():
                return True
        except Exception as e:
            logger.debug(f"Error validando cookie: {e}")
        return False

    def get_cookie_from_edge_profile(self) -> Optional[str]:
        try:
            logger.info("🧩 Intentando leer cookie de Steam desde Edge (browser_cookie3)...")
            cj = browser_cookie3.edge(domain_name='steamcommunity.com')
            for cookie in cj:
                if cookie.name == 'steamLoginSecure':
                    logger.info("✅ Cookie automática obtenida desde Edge (browser_cookie3).")
                    return cookie.value
            logger.info("⚠️ No se encontró cookie steamLoginSecure en perfiles accesibles por browser_cookie3.")
        except Exception as e:
            logger.debug(f"browser_cookie3 fallo: {e}")
        return None

    def get_cookie_with_selenium(self, headless: bool = False, profile_dir: str = "Default") -> Optional[str]:
        try:
            logger.info("🧩 Obteniendo cookie de Steam con Selenium (Edge)...")
            localapp = os.getenv("LOCALAPPDATA", "")
            user_data_dir = str(Path(localapp) / "Microsoft" / "Edge" / "User Data")
            if not Path(user_data_dir).exists():
                logger.error("❌ No se encontró la carpeta de perfiles de Edge.")
                return None

            options = Options()
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument(f"--profile-directory={profile_dir}")
            if headless:
                options.add_argument("--headless=new")

            driver = webdriver.Edge(service=service, options=options)
            driver.get("https://steamcommunity.com")
            cookies = driver.get_cookies()
            for c in cookies:
                if c.get('name') == 'steamLoginSecure':
                    val = c.get('value')
                    driver.quit()
                    save_cookie_to_env(val)
                    logger.debug(f"Cookie obtenida parcial: {val[:20]}... (longitud: {len(val)})")
                    logger.info("✅ Cookie obtenida con Selenium.")
                    return val
            driver.quit()
            logger.warning("⚠️ No se encontró 'steamLoginSecure' en la sesión de Steam.")
        except WebDriverException as e:
            msg = getattr(e, "msg", str(e))
            logger.error(f"❌ Selenium WebDriver error: {msg}")
        except Exception as e:
            logger.error(f"⚠️ Error inesperado obteniendo cookie con Selenium: {e}")
        return None

    def get_steam_cookie(self) -> Optional[str]:
        if self.env_cookie:
            logger.info("🧩 Validando cookie desde .env...")
            if self.validar_cookie(self.env_cookie):
                logger.info("✅ Cookie del .env válida.")
                return self.env_cookie
            else:
                logger.warning("⚠️ Cookie del .env expirada o inválida.")

        c = self.get_cookie_from_edge_profile()
        if c and self.validar_cookie(c):
            return c

        c2 = self.get_cookie_with_selenium(headless=False)
        if c2 and self.validar_cookie(c2):
            return c2

        logger.error("❌ No se pudo obtener cookie de Steam automáticamente.")
        return None
    def ask_and_obtain_cookie(self) -> Optional[str]:
        """
        Pregunta al usuario (terminal o GUI) si desea intentar obtener la cookie ahora.
        Si acepta, intenta primero browser_cookie3, luego Selenium.
        """
        try:
            should = False
            # Si hay terminal interactiva:
            if sys.stdin and sys.stdin.isatty():
                try:
                    res = input("La cookie de Steam es inválida o no existe. ¿Deseas intentar obtenerla ahora con Selenium/Edge? [y/N]: ").strip().lower()
                    should = res == "y" or res == "s"
                except Exception:
                    should = False
            else:
                # Intentar GUI simple con tkinter
                try:
                    import tkinter as tk
                    from tkinter import messagebox
                    root = tk.Tk()
                    root.withdraw()
                    should = messagebox.askyesno("Cookie inválida", "La cookie de Steam es inválida o no existe. ¿Deseas intentar obtenerla ahora?")
                    root.destroy()
                except Exception:
                    should = False

            if not should:
                logger.info("No se obtuvo cookie de Steam de forma interactiva.")
                return None

            # Intentos automáticos
            c = self.get_cookie_from_edge_profile()
            if c and self.validar_cookie(c):
                save_cookie_to_env(c)
                return c

            # intenta con selenium (abrirá Edge con tu perfil; pide interacción)
            c2 = self.get_cookie_with_selenium(headless=False)
            if c2 and self.validar_cookie(c2):
                save_cookie_to_env(c2)
                return c2

            logger.warning("No se pudo obtener cookie automáticamente tras solicitud del usuario.")
            return None
        except Exception as e:
            logger.error(f"Error en ask_and_obtain_cookie: {e}")
            return None

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
            logger.warning("⚠️ No se encontró GeForce NOW. Inícialo manualmente.")

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

class SteamScraper:
    def __init__(self, steam_cookie: Optional[str], test_rich_url: str):
        self.test_rich_url = test_rich_url
        self.session = requests.Session()
        if steam_cookie:
            self.session.cookies.set('steamLoginSecure', steam_cookie)
        self._last_presence = None

    def get_rich_presence(self) -> Optional[str]:
        if not self.test_rich_url:
            logger.debug("No TEST_RICH_URL configurada.")
            return None
        try:
            resp = self.session.get(self.test_rich_url, timeout=10)
            logger.debug(f"GET {self.test_rich_url} -> {resp.status_code}")
            if resp.status_code != 200:
                logger.debug("Status != 200 al obtener rich presence")
                return None
            if "Sign In" in resp.text or "login" in resp.url.lower():
                if not getattr(self, "_steam_expired_warned", False):
                    logger.warning("🔒 Sesión de Steam expirada.")
                    self._steam_expired_warned = True
                return None
            else:
                if getattr(self, "_steam_expired_warned", False):
                    logger.info("✅ Sesión de Steam restaurada.")
                    self._steam_expired_warned = False

            soup = BeautifulSoup(resp.text, 'html.parser')
            b = soup.find('b', string=re.compile(r'Localized Rich Presence Result', re.IGNORECASE))
            if not b:
                logger.debug("No se encontró tag esperado en la página de testing")
                return None
            text = (b.next_sibling or "").strip()
            if not text or "No rich presence keys set" in text:
                logger.debug("No hay rich presence definido para este usuario.")
                return None
            if text != self._last_presence:
                self._last_presence = text
                logger.info(f"🎮 Rich Presence (nuevo): {text}")
            else:
                logger.debug("Rich presence repetido; no se muestra en logs.")
            return text
        except Exception as e:
            logger.error(f"⚠️ Error scraping Steam: {e}")
            return None

def fetch_eos_presence(eos_presence_url: str = "http://localhost:5000/presence", timeout: float = 2.0):
    """Devuelve el JSON del endpoint /presence o None"""
    try:
        r = requests.get(eos_presence_url, timeout=timeout)
        if r.status_code != 200:
            logger.debug(f"EOS presence HTTP {r.status_code} from {eos_presence_url}")
            return None
        data = r.json()
        if not data or "error" in data:
            logger.debug(f"EOS presence empty or error: {data}")
            return None
        return data
    except Exception as e:
        logger.debug(f"No se pudo obtener EOS presence: {e}")
        return None

def fetch_eos_presence_via_rest(eos_token_url="http://localhost:5000/token"):
    """Obtiene el rich presence real usando la Web API de Epic si tienes un accessToken."""
    token_info = fetch_eos_token(eos_token_url)
    if not token_info or "accessToken" not in token_info or "accountId" not in token_info:
        logger.debug("No hay token o accountId en token_info.")
        return None

    access_token = token_info["accessToken"]
    account_id = token_info["accountId"]
    print("Account ID:", account_id)
    headers = {"Authorization": f"bearer {access_token}"}

    # URL hipotética; busca el endpoint real según tus permisos/pipeline en Epic Developer
    # Ejemplo genérico:
    presence_api_url = f"https://api.epicgames.dev/presence/v1/{account_id}"
    
    try:
        r = requests.get(presence_api_url, headers=headers, timeout=3)
        if r.status_code != 200:
            logger.debug(f"Epic presence API HTTP {r.status_code}")
            return None
        return r.json()
    except Exception as e:
        logger.debug(f"Error en Epic presence API: {e}")
        return None

def fetch_eos_token(eos_token_url: str = "http://localhost:5000/token", timeout: float = 2.0):
    """Devuelve el JSON del endpoint /token (accountId, accessToken, expiresAt) o None"""
    try:
        r = requests.get(eos_token_url, timeout=timeout)
        if r.status_code != 200:
            logger.debug(f"EOS token HTTP {r.status_code} from {eos_token_url}")
            return None
        data = r.json()
        if not data or "error" in data:
            logger.debug(f"EOS token empty or error: {data}")
            return None
        return data
    except Exception as e:
        logger.debug(f"No se pudo obtener EOS token: {e}")
        return None

def find_steam_appid_by_name(game_name: str) -> Optional[str]:
    try:
        url = f"https://steamcommunity.com/actions/SearchApps/{game_name}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, list):
                # Busca coincidencia exacta o la primera
                for app in data:
                    if app.get("name", "").lower() == game_name.lower():
                        return str(app.get("appid"))
                if data:
                    return str(data[0].get("appid"))
    except Exception as e:
        logger.error(f"Error buscando Steam AppID: {e}")
    return None

class PresenceManager:
    def __init__(self, client_id: str, games_map: Dict, cookie_manager: CookieManager, test_rich_url: str,
             update_interval: int = 10, keep_alive: bool = False,
             eos_presence_url: str = "http://localhost:5000/presence",
             eos_token_url: str = "http://localhost:5000/token"):
        atexit.register(self.close_fake_executable)

        # registrar cleanup en señales
        def _cleanup_and_exit(signum, frame):
            try:
                self.close_fake_executable()
            except Exception:
                pass
            sys.exit(0)

        signal.signal(signal.SIGTERM, _cleanup_and_exit)
        signal.signal(signal.SIGINT, _cleanup_and_exit)
        self.eos_presence_url = eos_presence_url
        self.eos_token_url = eos_token_url

        self.client_id_default = client_id
        self.games_map = games_map
        self.cookie_manager = cookie_manager
        self.test_rich_url = test_rich_url
        self.update_interval = update_interval
        self.keep_alive = keep_alive
        self.fake_proc = None
        self.fake_exec_path = None

        cookie = self.cookie_manager.get_steam_cookie()
        if not cookie:
            try:
                any_steam = any(
                    (v.get("appStore") or v.get("appStore", "")).strip().lower() == "steam"
                    or (v.get("steam_appid") is not None)
                    for v in (self.games_map or {}).values()
                )
            except Exception:
                any_steam = False

        if any_steam:
            cookie = self.cookie_manager.ask_and_obtain_cookie()
            self.scraper = SteamScraper(cookie, test_rich_url)
            if not self.client_id_default:
                raise RuntimeError("CLIENT_ID no configurado en .env")
            self.rpc = Presence(self.client_id_default)
            self._connect_rpc(self.client_id_default)
            self.last_game = None
            self.last_log_message = None

            if self.keep_alive:
                self._start_keep_alive_thread()

    def is_same_game(self, g1: Optional[dict], g2: Optional[dict]) -> bool:
        if g1 is None and g2 is None:
            return True
        if (g1 is None) != (g2 is None):
            return False
        for k in ("client_id", "executable_path", "name"):
            if g1.get(k) != g2.get(k):
                return False
        return True

    def wait_for_file_release(self, path: Path, timeout: float = 3.0) -> bool:
        start = time.time()
        if not path.exists():
            return True
        while time.time() - start < timeout:
            try:
                with open(path, "rb"):
                    return True
            except PermissionError:
                time.sleep(0.1)
            except Exception:
                return False
        return False

    def close_fake_executable(self):
        try:
            temp_dir_str = str(Path(tempfile.gettempdir()) / "discord_fake_game").lower()
            closed_any = False
            if self.fake_proc and self.fake_proc.poll() is None:
                logger.info(f"🛑 Cerrando ejecutable falso (PID {self.fake_proc.pid})")
                self.fake_proc.terminate()
                try:
                    self.fake_proc.wait(timeout=3)
                except Exception:
                    self.fake_proc.kill()
                closed_any = True
            for proc in psutil.process_iter(["exe", "pid"]):
                exe = proc.info.get("exe")
                if exe and exe.lower().startswith(temp_dir_str):
                    #logger.info(f"🛑 Cerrando ejecutable falso ({exe})")
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    closed_any = True
            if closed_any:
                time.sleep(0.35)
                logger.info("✅ Ejecutable falso cerrado")
        except Exception as e:
            logger.error(f"❌ Error cerrando ejecutable falso: {e}")
        finally:
            self.fake_proc = None
            self.fake_exec_path = None

    def launch_fake_executable(self, executable_path: str):
        try:
            temp_dir = Path(tempfile.gettempdir()) / "discord_fake_game"
            exec_full_path = temp_dir / executable_path
            exec_full_path.parent.mkdir(parents=True, exist_ok=True)

            if self.fake_exec_path == exec_full_path and self.fake_proc and self.fake_proc.poll() is None:
                logger.debug(f"🚀 Ejecutable ya en ejecución: {exec_full_path}")
                return
            dumb_path = BASE_DIR / "tools" / "dumb.exe"
            if not dumb_path.exists():
                logger.error(f"❌ dumb.exe no encontrado en {dumb_path}")
                return
            if not exec_full_path.exists():
                shutil.copy2(dumb_path, exec_full_path)
            else:
                if not self.wait_for_file_release(exec_full_path, timeout=3.0):
                    logger.error(f"❌ El archivo {exec_full_path} sigue bloqueado por otro proceso")
                    return
            logger.info(f"🚀 Ejecutando ejecutable falso: {exec_full_path}")
            proc = subprocess.Popen([str(exec_full_path)], cwd=str(exec_full_path.parent))
            self.fake_proc = proc
            self.fake_exec_path = exec_full_path
        except Exception as e:
            logger.error(f"❌ Error creando/ejecutando ejecutable falso: {e}")

    def update_presence(self, game_info: Optional[dict]):
        
        current_game = game_info or None
        game_changed = not self.is_same_game(self.last_game, current_game)
        
        status = None
        
        if current_game.get("appStore", "").lower() == "CUSTOM":
            logger.info("Intentando obtener presencia de EOS para juego Epic...")
            try:
                r = requests.get("http://localhost:5000/presence", timeout=3)
                if r.status_code == 200:
                    data = r.json()
                    pres = data.get("presence", {})
                    rich = pres.get("richText") or pres.get("RichText")
                    if rich:
                        status = rich 
                        self.log_once(f"🔁 Usando EOS Presence: {status}")
                        current_game["image"] = current_game.get("image", "epic")
            except Exception as e:
                logger.error(f"No se pudo obtener EOS presence: {e}")
        if current_game and current_game.get("name") is None:
            self.log_once("🛑 GeForce NOW está cerrado")
            self.close_fake_executable()
            try:
                self.rpc.clear()
            except Exception:
                pass
            self.last_game = None
            return
        
            # ⚡ Opción B: intentar relanzar automáticamente GeForce NOW
            # AppLauncher.launch_geforce_now()

        if current_game and current_game.get("name") == "":
            self.log_once("🔄 En el menú")
            rn = "geforce now"
            current_game["name"] = "GeForce NOW"
            current_game["image"] = "lib"

        if game_changed:
            self.close_fake_executable()
            if current_game and current_game.get("executable_path"):
                self.launch_fake_executable(current_game["executable_path"])

        if not current_game:
            if self.last_game is not None:
                try:
                    self.rpc.clear()
                except Exception:
                    pass
                self.last_game = None
            return

        client_id = current_game.get("client_id", self.client_id_default)
        if getattr(self.rpc, "client_id", None) != client_id:
            try:
                self.rpc.clear()
                self.rpc.close()
            except Exception:
                pass
            if client_id:
                self._connect_rpc(client_id)
                #self.log_once(f"🔁 Cambiado client_id a {client_id}")

        if status is None:
            status = self.scraper.get_rich_presence() if current_game.get('steam_appid') else None

        has_custom = current_game.get("client_id") and current_game.get("client_id") != self.client_id_default
        if has_custom:
            self.log_once(f"🔄 iniciando presencia para: {current_game.get('name', 'Desconocido')}")
        else:
            if current_game.get("name") != "GeForce NOW":
                self.log_once(f"🔄 Usando client_id por defecto para: {current_game.get('name')}")
        def split_status(s):
            for sep in ["|", " - ", ":", "›", ">"]:
                if sep in s:
                    a, b = s.split(sep, 1)
                    return a.strip(), b.strip()
            return s.strip(), None

        details, state = (split_status(status) if status else (None, None))
        if not details and not has_custom:
            rn = current_game.get('name', '').strip().lower()
            details = "Buscando qué jugar" if rn in ["geforce now", "Games", ""] else f"Jugando a {current_game.get('name')}"
            if rn in ["geforce now", "Games", ""]:
                current_game["image"] = "lib"

        presence_data = {
            "details": details,
            "state": state,
            "large_image": current_game.get('image', 'steam'),
            "large_text": current_game.get('name'),
            "small_image": current_game.get("icon_key") if current_game.get("icon_key") else None
        }
        try:
            self.rpc.update(**{k: v for k, v in presence_data.items() if v})
        except Exception as e:
            logger.error(f"❌ Error actualizando Presence: {e}")
            if "pipe was closed" in str(e).lower():
                try:
                    self._connect_rpc(client_id) 
                    logger.info("🔁 Reconectado con Discord RPC tras cierre de pipe")
                except Exception as e2:
                    logger.error(f"❌ Falló la reconexión a Discord RPC: {e2}")


        self.last_game = dict(current_game) if isinstance(current_game, dict) else current_game

    def is_geforce_running(self) -> bool:
        try:
            for proc in psutil.process_iter(attrs=['name']):
                name = (proc.info.get('name') or "").lower()
                if "geforcenow" in name:
                    return True
        except Exception as e:
            logger.debug(f"Error comprobando procesos: {e}")
        return False

    def _connect_rpc(self, client_id):
        try:
            self.rpc = Presence(client_id)
            self.rpc.connect()
            logger.info("✅ Discord RPC conectado correctamente")
        except Exception as e:
            logger.error(f"❌ Error al conectar con Discord ({client_id}): {e}")

    def log_once(self, msg, level="info"):
        if msg != self.last_log_message:
            getattr(logger, level)(msg)
            self.last_log_message = msg

    def find_active_game(self) -> Optional[dict]:
        try:
            import win32gui, win32process # type: ignore
            hwnds = []
            win32gui.EnumWindows(lambda h, p: p.append(h) if win32gui.IsWindowVisible(h) else None, hwnds)
            last_title = getattr(self, "_last_window_title", None)
            title = None
            for hwnd in hwnds:
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc_name = psutil.Process(pid).name().lower()
                except Exception:
                    continue
                if "geforcenow" not in proc_name:
                    continue
                title = win32gui.GetWindowText(hwnd)
                if title == last_title:
                
                    pass
                else:
                    setattr(self, "_last_window_title", title)
                if title == None:
                    self.log_once("⚠️ GeForce NOW no está abierto")
                logger.debug(f"Juego activo detectado: {title}")
                clean = re.sub(r'\s*(en|on|via)?\s*GeForce\s*NOW.*$', '', title, flags=re.IGNORECASE).strip()
                clean = re.sub(r'[®™]', '', clean).strip()
                if clean.lower() not in ["geforce now", "games", ""]:
                    logger.debug(f"Juego limpio: {clean}")

                
                last_clean = getattr(self, "_last_clean_title", None)
                if clean != last_clean:
                    setattr(self, "_last_clean_title", clean)
                appid = None 
                for game_name, info in self.games_map.items():
                    if clean.lower() == game_name.lower():
                        if not info.get("steam_appid"):
                            appid = find_steam_appid_by_name(clean)
                            if appid:
                                info["steam_appid"] = appid
                                config_path = CONFIG_PATH_FILE.read_text(encoding="utf-8").strip()
                                config_path = Path(config_path)
                                games_config = safe_json_load(config_path) or {}
                                games_config[game_name]["steam_appid"] = appid
                                save_json(games_config, config_path)
                                logger.info(f"✅ Steam AppID actualizado en JSON para: {game_name} -> {appid}")
                                self.games_map = games_config
                        return info
                appid = find_steam_appid_by_name(clean)
                new_game = {
                    "name": clean,
                    "steam_appid": appid,
                    "client_id": self.client_id_default,
                    "image": "steam"
                }
                self.games_map[clean] = new_game
                config_path = CONFIG_PATH_FILE.read_text(encoding="utf-8").strip()
                config_path = Path(config_path)
                games_config = safe_json_load(config_path) or {}
                games_config[clean] = new_game
                save_json(games_config, config_path)
                logger.info(f"🆕 Juego agregado a config: {clean} (AppID: {appid})")
                self.games_map = games_config
                return new_game
            return {'name': title, 'image': 'geforce_default', 'client_id': self.client_id_default}
        except Exception as e:
            if str(e) == "cannot access local variable 'title' where it is not associated with a value":
                self.log_once(f"⚠️ GeForce NOW está cerrado")
            else:
                logger.error(f"⚠️ Error detectando juego activo: {e}")

    def _start_keep_alive_thread(self):
        def keepalive():
            try:
                import pyautogui #type: ignore
            except Exception:
                logger.warning("pyautogui no disponible; keep-alive deshabilitado.")
                return
            logger.info("🔔 Keep-alive activado (movimientos de 1 px cada 5 min).")
            while True:
                try:
                    pyautogui.moveRel(1, 0, duration=0.1)
                    pyautogui.moveRel(-1, 0, duration=0.1)
                    time.sleep(300)
                except Exception as e:
                    self.log_once("⚠️ pyautogui alcanzó el limite de la pantalla")


        t = threading.Thread(target=keepalive, daemon=True)
        t.start()

    def run_loop(self):
        logger.info("🟢 Iniciando monitor de presencia...")
        try:
            while True:
                time.sleep(self.update_interval)
                if not self.is_geforce_running():
                    if self.last_game is not None:
                        logger.info("⚠️ GeForce NOW no está en ejecución — limpiando presencia y estado local.")
                        try:
                            self.rpc.clear()
                        except Exception:
                            pass
                        self.close_fake_executable()
                        self.last_game = None
                        self.last_log_message = None
                    time.sleep(self.update_interval)
                    continue

                game = self.find_active_game()
                self.update_presence(game)
                time.sleep(self.update_interval)

        except KeyboardInterrupt:
            logger.info("🔴 Detenido por usuario")
        except Exception as e:
            if str(e) != "'NoneType' object has no attribute 'get'" and str(e) != "cannot access local variable 'title' where it is not associated with a value":
                logger.error(f"❌ Error inesperado en el loop principal: {e}")
            try:
                self.rpc.clear()
            except Exception:
                pass
            try:
                self.rpc.close()
            except Exception:
                pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-launch-geforce", action="store_true")
    parser.add_argument("--no-launch-discord", action="store_true")
    parser.add_argument("--verbose", action="store_true", help="Mostrar lista completa de juegos en carga")
    parser.add_argument("--no-keepalive", action="store_true", help="Desactivar keep-alive (si está activado)")
    args = parser.parse_args()

    cfgm = ConfigManager(CONFIG_PATH_FILE)
    games = cfgm.get_game_mapping()

    if not args.no_launch_discord:
        AppLauncher.launch_discord()
    if not args.no_launch_geforce:
        AppLauncher.launch_geforce_now()

    cookie_mgr = CookieManager(env_cookie=STEAM_COOKIE_ENV, test_url=TEST_RICH_URL)
    presence = PresenceManager(client_id=CLIENT_ID, games_map=games, cookie_manager=cookie_mgr,
                           test_rich_url=TEST_RICH_URL, update_interval=UPDATE_INTERVAL,
                           keep_alive=(not args.no_keepalive),
                           eos_presence_url="http://localhost:5000/presence",
                           eos_token_url="http://localhost:5000/token")

    presence.run_loop()

if __name__ == "__main__":
    main()

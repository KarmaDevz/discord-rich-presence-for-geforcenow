#!/usr/bin/env python3
import argparse
import atexit
import threading, time
import json
import difflib
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
import asyncio
import inspect
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import winreg

import concurrent.futures
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
import pystray
from PIL import Image, ImageDraw

logger = logging.getLogger("geforce_presence")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(ch)
LOCK_FILE = Path(tempfile.gettempdir()) / "geforce_presence.lock"
# --- Globals para callbacks del tray ---
PRESENCE_INSTANCE = None   # Se asigna en main() con PresenceManager
COOKIE_MANAGER = None      # Se asigna en main() con CookieManager
PYSTRAY_AVAILABLE = True
_tray_icon = None
_tray_thread = None
_tray_stop_event = threading.Event()

def start_tray_icon(on_quit_callback, title="GeForceNOW Presence"):
    img_path = ASSETS_DIR / "geforce.ico"

    global _tray_icon, _tray_thread, _tray_stop_event, PRESENCE_INSTANCE, COOKIE_MANAGER
    try:
        title = TEXTS.get('tray_title', title)
    except Exception:
        pass
    if not PYSTRAY_AVAILABLE:
        logger.info("pystray/Pillow no disponibles; no se mostrará icono en bandeja.")
        return False

    # --- Funciones de callback actualizadas ---
    def _quit_action(icon, item):
        logger.info("Cierre pedido desde icono de bandeja.")
        try:
            release_lock()
        except Exception:
            pass
        try:
            icon.visible = False
            icon.stop()
        except Exception:
            pass
        try:
            if PRESENCE_INSTANCE is not None:
                PRESENCE_INSTANCE.close()
        except Exception:
            pass
        os._exit(0)

    def _open_logs(icon, item):
        try:
            os.startfile(str(LOG_FILE))
        except Exception as e:
            logger.debug(f"No se pudo abrir logs: {e}")

    def _open_geforce(icon, item=None):
        try:
            AppLauncher.launch_geforce_now()
        except Exception as e:
            logger.debug(f"Error abriendo GeForce NOW: {e}")

    def _obtain_cookie(icon, item):
        try:
            if COOKIE_MANAGER is None:
                show_message("Error", "Cookie manager no disponible.", kind="error")
                return
            
            # Crear ventana raíz con icono en barra de tareas
            root = create_root_window("Obtain Steam Cookie")
            root.deiconify()  # Mostrar la ventana para que aparezca en barra de tareas
            
            val = COOKIE_MANAGER.ask_and_obtain_cookie()
            
            if val:
                save_cookie_to_env(val)
                show_message("OK", "Steam cookie guardada.", kind="info")

                # 🔁 Refrescar presencia sin reiniciar el programa
                if PRESENCE_INSTANCE is not None:
                    PRESENCE_INSTANCE.cookie_manager.env_cookie = val
                    PRESENCE_INSTANCE.scraper = SteamScraper(val, PRESENCE_INSTANCE.test_rich_url)
                    logger.info("🔁 SteamScraper actualizado con nueva cookie.")
            else:
                show_message("Error", "No se pudo obtener la cookie.", kind="error")
                
            root.destroy()
        except Exception as e:
            show_message("Error", f"Fallo al obtener cookie: {e}", kind="error")

    def _toggle_force_game(icon, item):
        """Función unificada para forzar o detener el forzado de juego"""
        if PRESENCE_INSTANCE is None:
            show_message("Error", "Presencia no inicializada.", kind="error")
            return

        # Si ya hay un juego forzado, detenerlo
        if PRESENCE_INSTANCE.forced_game:
            PRESENCE_INSTANCE.stop_force_game()
            show_message("OK", "Forzado de juego detenido.", kind="info")
            return

        # Si no hay juego forzado, iniciar el proceso de forzar juego
        from tkinter import simpledialog
        
        # Crear ventana raíz principal
        root = create_root_window("Force Game")
        root.deiconify()  # Mostrar en barra de tareas
        
        try:
            # --- Pedir nombre del juego ---
            game_name = simpledialog.askstring("Forzar juego", "Nombre del juego:", parent=root)
            if not game_name:
                root.destroy()
                return

            gm = PRESENCE_INSTANCE.games_map or {}
            candidates = [k for k in gm if game_name.lower() in k.lower()]

            options = []
            if candidates:
                # Coincidencias en JSON
                for k in candidates:
                    options.append((k, gm[k].get("client_id"), gm[k].get("executable_path")))
            else:
                # Buscar en Discord
                disc = PRESENCE_INSTANCE._find_discord_matches(game_name, max_candidates=5)
                for c in disc:
                    options.append((c["name"], c["id"], c.get("exe")))
                    PRESENCE_INSTANCE._apply_discord_match(game_name, c)

            if not options:
                show_message("Info", "Sin coincidencias en JSON ni Discord.")
                root.destroy()
                return

            # --- Crear ventana de selección como diálogo modal ---
            top = create_modal_dialog(root, "Seleccionar juego")
            
            tk.Label(top, text="Selecciona una coincidencia:").pack(padx=10, pady=(8, 4))

            lb = tk.Listbox(top, width=80, height=min(10, len(options)))
            for name, cid, exe in options:
                lb.insert(tk.END, f"{name} — id={cid}")
            lb.pack(padx=10, pady=10)

            sel = {"v": None}

            def ok():
                if lb.curselection():
                    idx = lb.curselection()[0]
                    sel["v"] = options[idx]
                    top.destroy()

            def cancel():
                sel["v"] = None
                top.destroy()

            btn_frame = tk.Frame(top)
            tk.Button(btn_frame, text="Aceptar", command=ok).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Cancelar", command=cancel).pack(side="left")
            btn_frame.pack(pady=(0, 10))

            # Configurar comportamiento al cerrar
            top.protocol("WM_DELETE_WINDOW", cancel)
            
            # Establecer foco en el Listbox
            lb.focus_set()
            lb.selection_set(0)  # Seleccionar primer elemento por defecto

            # Esperar hasta que el usuario cierre el diálogo
            root.wait_window(top)

            if not sel["v"]:
                root.destroy()
                return

            # --- Aplicar selección ---
            name, cid, exe = sel["v"]
            
            if cid:
                # Desconectamos RPC temporalmente antes de forzar el nuevo juego
                try:
                    def reconnect_after_delay():
                        time.sleep(11)  # esperar 11 segundos (intervalo desfasado)
                    PRESENCE_INSTANCE.rpc.close()
                    logger.info("📴 RPC desconectado temporalmente (modo forzar juego).")
                except Exception:
                    pass

                try:
                    PRESENCE_INSTANCE.client_id = cid
                    PRESENCE_INSTANCE._connect_rpc(cid)
                    logger.info(f"🔁 RPC reconectado con client_id forzado: {cid}")
                except Exception as e:
                    logger.error(f"❌ Error reconectando RPC tras forzar juego: {e}")
                    threading.Thread(target=reconnect_after_delay, daemon=True).start()

            if exe:
                try:
                    PRESENCE_INSTANCE.close_fake_executable()
                except Exception as e:
                    logger.debug(f"No se pudo cerrar ejecutable previo: {e}")
                PRESENCE_INSTANCE.launch_fake_executable(exe)

            PRESENCE_INSTANCE.forced_game = {
                "name": name,
                "client_id": cid,
                "executable_path": exe
            }
            PRESENCE_INSTANCE.last_game = dict(PRESENCE_INSTANCE.forced_game)
            logger.info(f"🎮 Juego forzado activado: {name} (id={cid})")

            show_message("OK", f"Juego forzado: {name}", kind="info")

        except Exception as e:
            show_message("Error", f"Ocurrió un error: {e}", kind="error")
        finally:
            try:
                root.destroy()
            except:
                pass

    def _get_force_game_text(icon=None, item=None):
        """Devuelve el texto dinámico para el ítem del menú (compatible con pystray)"""
        if PRESENCE_INSTANCE and PRESENCE_INSTANCE.forced_game:
            game_name = PRESENCE_INSTANCE.forced_game.get('name', 'Unknown')
            # Acortar el nombre si es muy largo
            if len(game_name) > 20:
                game_name = game_name[:17] + "..."
            return f"Stop forcing: {game_name}"
        else:
            return TEXTS.get("tray_force_game", "Force game...")

    # --- crear menú dinámico ---
    def create_dynamic_menu():
        """Crea el menú dinámico basado en el estado actual"""
        return pystray.Menu(
            pystray.MenuItem(_get_force_game_text, _toggle_force_game),
            pystray.MenuItem(TEXTS.get("tray_get_cookie", "Obtain Steam cookie"), _obtain_cookie),
            pystray.MenuItem(TEXTS.get("tray_open_geforce", "Open GeForce NOW"), _open_geforce),
            pystray.MenuItem(TEXTS.get("tray_open_logs", "Open logs"), _open_logs),
            pystray.MenuItem(TEXTS.get("tray_exit", "Exit"), _quit_action),
        )

    try:
        icon = pystray.Icon("geforce_presence", Image.open(str(img_path)), title, menu=create_dynamic_menu())
    except Exception as e:
        logger.error(f"No se pudo crear Icon pystray: {e}")
        return False

    # Función para actualizar el menú periódicamente
    def update_menu_periodically():
        while not _tray_stop_event.is_set():
            try:
                if _tray_icon:
                    _tray_icon.update_menu()
            except Exception as e:
                logger.debug(f"Error actualizando menú: {e}")
            time.sleep(2)  # Actualizar cada 2 segundos

    # doble-click (si backend lo soporta)
    try:
        listener = getattr(icon, "_listener", None)
        if listener:
            listener.on_double_click = lambda icon, item: AppLauncher.launch_geforce_now()
    except Exception:
        pass

    def run_icon(): 
        try: 
            icon.run()
        except Exception as e: 
            logger.debug(f"Icon tray error: {e}")

    _tray_icon = icon
    _tray_thread = threading.Thread(target=run_icon, daemon=True)
    _tray_thread.start()
    
    # Iniciar hilo para actualizar el menú periódicamente
    menu_updater_thread = threading.Thread(target=update_menu_periodically, daemon=True)
    menu_updater_thread.start()
    
    return True

# ----------------- Helpers & resource paths -----------------
def resource_path(*parts):
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        base = Path(__file__).resolve().parent.parent
    return base.joinpath(*parts)

BASE_DIR = resource_path("")      
CONFIG_DIR = resource_path("config")
LOGS_DIR = resource_path("logs")
LANG_DIR = resource_path("lang")
ASSETS_DIR = resource_path("assets")
driver_path = resource_path("tools", "msedgedriver.exe")
LOG_FILE = LOGS_DIR / "geforce_presence.log"
ENV_PATH = resource_path(".env")
DISCORD_DETECTABLE_URL = "https://discord.com/api/v9/applications/detectable"
DISCORD_CACHE_PATH = LOGS_DIR / "discord_apps_cache.json"
DISCORD_CACHE_TTL = 60 * 60
DISCORD_AUTO_APPLY_THRESHOLD = 0.88  
DISCORD_ASK_TIMEOUT = 30  
DEFAULT_ENV_CONTENT = """CLIENT_ID = '1095416975028650046'
UPDATE_INTERVAL = 10
CONFIG_PATH_FILE = ''
TEST_RICH_URL = 'https://steamcommunity.com/dev/testrichpresence'
STEAM_COOKIE=''
"""

def get_lang_from_registry(default="en"):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\GeForcePresence")
        lang, _ = winreg.QueryValueEx(key, "lang")
        winreg.CloseKey(key)

        if "spanish" in lang.lower():
            return "es"
        elif "english" in lang.lower():
            return "en"
        else:
            return default
    except Exception:
        return default

def load_locale(lang: str = "en") -> dict:
    path = LANG_DIR / f"{lang}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads((LANG_DIR / "en.json").read_text(encoding="utf-8"))


try:
    LANG = get_lang_from_registry()
    TEXTS = load_locale(LANG)
except Exception:
    LANG = os.getenv('GEFORCE_LANG', 'en')
    TEXTS = load_locale(LANG)






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

def create_root_window(title="GeForceNOW Presence"):
    """Crea una ventana raíz configurada para diálogos con icono en barra de tareas"""
    root = tk.Tk()
    root.iconbitmap(default=str(ASSETS_DIR / "geforce.ico"))
    root.title(title)
    root.withdraw()  # Ocultar la ventana principal pero mantener el icono
    return root

def create_modal_dialog(parent, title):
    """Crea un diálogo modal con mejor manejo para Windows 11"""
    dialog = tk.Toplevel(parent)
    dialog.iconbitmap(default=str(ASSETS_DIR / "geforce.ico"))
    dialog.title(title)
    dialog.transient(parent)  # Establece relación padre-hijo
    dialog.grab_set()  # Hace el diálogo modal
    dialog.lift()
    dialog.focus_force()
    
    # Centrar en la pantalla
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - dialog.winfo_width()) // 2
    y = parent.winfo_y() + (parent.winfo_height() - dialog.winfo_height()) // 2
    dialog.geometry(f"+{x}+{y}")
    
    return dialog

def show_message(title: str, message: str, kind: str = "info") -> None:
    """Versión mejorada para Windows 11 que mantiene el foco"""
    root = create_root_window(title)
    
    # Configuración específica para Windows 11
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()
    
    try:
        if kind == "info":
            messagebox.showinfo(title, message, parent=root)
        elif kind == "warning":
            messagebox.showwarning(title, message, parent=root)
        elif kind == "error":
            messagebox.showerror(title, message, parent=root)
        elif kind == "askyesno":
            return messagebox.askyesno(title, message, parent=root)
    except Exception as e:
        logger.error(f"Error mostrando mensaje: {e}")
    finally:
        try:
            root.destroy()
        except:
            pass

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


def acquire_lock() -> bool:
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())

            if psutil.pid_exists(pid):
                logger.warning(f"⚠️ Ya existe otra instancia (PID {pid}). Reiniciando...")
                try:
                    # Cierra la instancia anterior (si es posible)
                    p = psutil.Process(pid)
                    p.terminate()
                    p.wait(5)
                    logger.info("✅ Instancia anter_ior finalizada correctamente.")
                except Exception as e:
                    logger.error(f"No se pudo cerrar la instancia anterior: {e}")
                
                time.sleep(2)

                try:
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                except Exception as e:
                    logger.error(f"No se pudo reiniciar el programa: {e}")
                    sys.exit(1)

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

# ----------------- JSON utils -----------------
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

# ----------------- Notifications -----------------
def notify_background(message=None, title=None, timeout=5):
    if title is None:
        title = TEXTS.get("notify_title", "GeForce NOW Presence")
    if message is None:
        message = TEXTS.get("notify_background", "The program is running in the background")
    """
    No system notifications (pystray-only). Logs the background status.
    """
    logger.info(f"{title}: {message} (no notification shown, tray-only)")


# ----------------- Instance detection -----------------
def find_other_instance() -> Optional[psutil.Process]:
    """
    Detecta si hay otra instancia de este mismo script/exe corriendo.
    Retorna proceso encontrado o None.
    """
    try:
        current_pid = os.getpid()
        current_file = Path(sys.argv[0]).resolve()

        for proc in psutil.process_iter(['pid', 'exe', 'cmdline']):
            if proc.info['pid'] == current_pid:
                continue

            cmdline = proc.info.get('cmdline') or []
            exe = proc.info.get('exe')


            if exe:
                try:
                    if Path(exe).resolve() == current_file:
                        return proc
                except Exception:
                    pass


            for arg in cmdline:
                try:
                    if Path(arg).resolve() == current_file:
                        return proc
                except Exception:
                    continue
    except Exception as e:
        logger.debug(f"Error buscando otras instancias: {e}")
    return None

# ----------------- Tray icon management -----------------
_tray_icon = None
_tray_thread = None
_tray_stop_event = threading.Event()

def _create_default_icon_image(size=64):

    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    r = size // 2
    d.ellipse((4, 4, size-4, size-4), fill=(20, 100, 200, 255))
    d.text((size*0.28, size*0.18), "G", fill=(255,255,255,255))
    return img


def stop_tray_icon():
    global _tray_icon, _tray_thread
    _tray_stop_event.set()  # Detener el hilo de actualización
    try:
        if _tray_icon:
            try:
                _tray_icon.stop()
            except Exception:
                pass
            _tray_icon = None
    except Exception:
        pass

# ----------------- AppMonitor, ConfigManager, CookieManager, etc. (copiado y adaptado) -----------------
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
                show_message("Error", TEXTS.get('error_no_config', 'No configuration file found. Please select one.'), kind="error")
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
    
    def ask_get_cookie(self) -> bool:
        """Pregunta al usuario si quiere obtener la cookie de Steam."""
        res =show_message("Cookie", TEXTS.get('ask_cookie', 'The program will try to obtain your Steam cookie using Microsoft Edge. Make sure you are logged in to Steam in Edge.\n\nDo you want to continue?'), kind="askyesno")
        return res
    
    def close_edge_processes(self):
        """Cierra todos los procesos de Microsoft Edge."""
        import psutil
        closed = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and "msedge.exe" in proc.info['name'].lower():
                    proc.terminate()
                    closed += 1
            except Exception:
                continue
        if closed:
            logger.info(f"🔒 {closed} procesos de Edge terminados.")
        else:
            logger.debug("No había procesos de Edge en ejecución.")

    def get_cookie_with_selenium(self, headless: bool = False, profile_dir: str = "Default") -> Optional[str]:
        try:
            res = self.ask_get_cookie()
            if not res:
                logger.info("⏭️ Usuario eligió no obtener cookie de Steam.")
                return None

            import psutil
            edge_running = any(
                (p.info['name'] and "msedge.exe" in p.info['name'].lower())
                for p in psutil.process_iter(['name'])
            )

            if edge_running:
                res = show_message("Edge abierto", TEXTS.get('edge_open_confirm'), kind="askyesno")

                if not res:
                    logger.info("⏭️ Usuario canceló la obtención de cookie porque Edge estaba abierto.")
                    return None

                self.close_edge_processes()
                time.sleep(2)


            logger.info("🧩 Obteniendo cookie de Steam con Selenium (Edge)...")
            ...

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
        """Versión mejorada para Windows 11"""
        try:
            should = show_message("Cookie", 
                                TEXTS.get('ask_cookie', 'The program will try to obtain your Steam cookie using Microsoft Edge. Make sure you are logged in to Steam in Edge.\n\nDo you want to continue?'), 
                                kind="askyesno")

            if not should:
                logger.info("No se obtuvo cookie de Steam de forma interactiva.")
                return None

            # Resto del código igual...
            c = self.get_cookie_from_edge_profile()
            if c and self.validar_cookie(c):
                save_cookie_to_env(c)
                return c

            c2 = self.get_cookie_with_selenium(headless=False)
            if c2 and self.validar_cookie(c2):
                save_cookie_to_env(c2)
                return c2

            logger.warning("No se pudo obtener cookie automáticamente tras solicitud del usuario.")
            return None
            
        except Exception as e:
            logger.error(f"Error en ask_and_obtain_cookie: {e}")
            return None
# ----------------- AppLauncher, SteamScraper, PresenceManager (sin cambios funcionales importantes) -----------------
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
            show_message("Error", TEXTS.get('geforce_not_found', 'GeForce NOW not found in the default installation path.'), kind="error")
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
        self._last_group_size = None
    
    def get_rich_presence(self) -> tuple[Optional[str], Optional[int]]:
        """
        Retorna una tupla (rich_presence_text, group_size)
        """
        if not self.test_rich_url:
            logger.debug("No TEST_RICH_URL configurada.")
            return None, None
        
        try:
            resp = self.session.get(self.test_rich_url, timeout=10)
            if resp.status_code != 200:
                logger.debug("Status != 200 al obtener rich presence")
                return None, None
            
            if "Sign In" in resp.text or "login" in resp.url.lower():
                if not getattr(self, "_steam_expired_warned", False):
                    logger.warning("🔒 Sesión de Steam expirada.")
                    self._steam_expired_warned = True
                return None, None
            else:
                if getattr(self, "_steam_expired_warned", False):
                    logger.info("✅ Sesión de Steam restaurada.")
                    self._steam_expired_warned = False

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 1. Obtener el texto de Rich Presence (filtrando los que contienen '#')
            b = soup.find('b', string=re.compile(r'Localized Rich Presence Result', re.IGNORECASE))
            rich_presence_text = None
            if b:
                text = (b.next_sibling or "").strip()
                if text and "No rich presence keys set" not in text:
                    # Filtrar texto que contiene '#'
                    if '#' not in text:
                        rich_presence_text = text
                        if text != self._last_presence:
                            self._last_presence = text
                            logger.info(f"🎮 Rich Presence (nuevo): {text}")
                    else:
                        logger.debug(f"❌ Rich Presence filtrado (contiene '#'): {text}")
                        rich_presence_text = None
            
            # 2. Extraer steam_player_group_size
            group_size = self._extract_group_size(soup)
            
            return rich_presence_text, group_size
            
        except Exception as e:
            logger.error(f"⚠️ Error scraping Steam: {e}")
            return None, None
    
    def _extract_group_size(self, soup) -> Optional[int]:
        """
        Extrae el valor de steam_player_group_size de la tabla HTML
        """
        try:
            # Buscar la fila que contiene 'steam_player_group_size'
            rows = soup.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    first_cell_text = cells[0].get_text().strip()
                    if 'steam_player_group_size' in first_cell_text:
                        # El valor está en la segunda celda
                        group_size_text = cells[1].get_text().strip()
                        if group_size_text.isdigit():
                            group_size = int(group_size_text)
                            if group_size != self._last_group_size:
                                self._last_group_size = group_size
                                logger.info(f"👥 Group size detectado: {group_size}")
                            return group_size
            
            # Si no se encuentra steam_player_group_size, buscar patrones alternativos
            group_size = self._find_alternative_group_size(soup)
            return group_size
            
        except Exception as e:
            logger.debug(f"Error extrayendo group size: {e}")
            return None
    
    def _find_alternative_group_size(self, soup) -> Optional[int]:
        """
        Busca el group size usando métodos alternativos (XPath simulation)
        """
        try:
            # Método 1: Buscar en todas las celdas que puedan contener números de grupo
            cells = soup.find_all('td')
            for cell in cells:
                text = cell.get_text().strip()
                # Buscar patrones como "1/4", "2 players", etc.
                if '/' in text and text.replace('/', '').isdigit():
                    parts = text.split('/')
                    if len(parts) == 2 and parts[0].isdigit():
                        current_players = int(parts[0])
                        logger.info(f"👥 Group size alternativo detectado: {current_players}")
                        return current_players
            
            # Método 2: Buscar números que representen cantidad de jugadores
            for cell in cells:
                text = cell.get_text().strip()
                if text.isdigit():
                    num = int(text)
                    if 1 <= num <= 16:  # Rango razonable para grupos de juego
                        logger.info(f"👥 Group size numérico detectado: {num}")
                        return num
            
            return None
        except Exception as e:
            logger.debug(f"Error en búsqueda alternativa de group size: {e}")
            return None
            
def find_steam_appid_by_name(game_name: str) -> Optional[str]:
    try:
        url = f"https://steamcommunity.com/actions/SearchApps/{game_name}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, list):

                for app in data:
                    if app.get("name", "").lower() == game_name.lower():
                        return str(app.get("appid"))
                if data:    
                    return str(data[0].get("appid"))
    except Exception as e:
        logger.error(f"Error buscando Steam AppID: {e}")
    return None

class PresenceManager:
    def __init__(self, client_id: str, games_map: dict, cookie_manager, test_rich_url: str,
                 update_interval: int = 10, keep_alive: bool = False):
        import atexit, signal, sys

        self.client_id = client_id
        self.games_map = games_map
        self.cookie_manager = cookie_manager
        self.test_rich_url = test_rich_url
        self.update_interval = update_interval
        self.keep_alive = keep_alive
        self.fake_proc = None
        self.fake_exec_path = None
        self.last_log_message = None
        self.rpc = Presence(self.client_id)
        self._connect_rpc()

        self.scraper = SteamScraper(self.cookie_manager.env_cookie, test_rich_url)

        self.last_game = None
        self.forced_game = None


        atexit.register(self.close)
        signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
        signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    def _connect_rpc(self, client_id: Optional[str] = None):
        try:
            try:
                self.rpc.close()
            except Exception:
                pass
            client_id = client_id or self.client_id
            self.rpc = Presence(client_id)
            self.rpc.connect()
            logger.info(f"✅ Conectado a Discord RPC con client_id={client_id}")
        except Exception as e:
            logger.error(f"❌ Error conectando a Discord RPC: {e}")
            self.rpc = None
    
    def stop_force_game(self):
        """Detiene el forzado de juego y vuelve a la detección automática"""
        if self.forced_game:
            forced_game_name = self.forced_game.get('name', 'Unknown')
            logger.info(f"🧹 Deteniendo forzado de juego: {forced_game_name}")
            
            # Guardar el juego forzado para evitar reconexión automática
            self._last_forced_game = self.forced_game.copy()
            self.forced_game = None
            self.last_game = None
            
            # Cerrar el ejecutable falso
            self.close_fake_executable()
            
            # Desconectar RPC para reconectar con el client_id por defecto
            try:
                self.rpc.close()
            except Exception:
                pass
            
            # Reconectar con el client_id por defecto
            self.client_id = "1095416975028650046"  # Client ID por defecto
            self._connect_rpc(self.client_id)
            
            # Establecer un temporizador para evitar reconexión automática inmediata
            self._force_stop_time = time.time()
            
            logger.info("🔄 Volviendo a detección automática de juegos")

    def _disconnect_rpc_temporarily(self):
        """Desconecta el RPC temporalmente (sin limpiar presencia)."""
        try:
            if self.rpc:
                self.rpc.close()
                self.rpc = None
                logger.info("📴 RPC desconectado temporalmente (modo forzar juego activo).")
        except Exception as e:
            logger.debug(f"Error al desconectar RPC temporalmente: {e}")

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

    def _fetch_discord_apps_cached(self):
        """Devuelve la lista de apps desde caché o descarga si expiró."""
        try:
            if DISCORD_CACHE_PATH.exists():
                data = safe_json_load(DISCORD_CACHE_PATH)
                if data and isinstance(data, dict):
                    ts = data.get("_ts", 0)
                    if time.time() - ts < DISCORD_CACHE_TTL:
                        return data.get("apps", [])

            resp = requests.get(DISCORD_DETECTABLE_URL, timeout=15)
            if resp.status_code == 200:
                apps = resp.json()
                to_save = {"_ts": int(time.time()), "apps": apps}
                try:
                    save_json(to_save, DISCORD_CACHE_PATH)
                except Exception:
                    pass
                return apps
        except Exception as e:
            logger.debug(f"Error obteniendo detectable de Discord: {e}")
        return []

    def _find_discord_matches(self, game_name: str, max_candidates: int = 5):
        """Busca coincidencias por name o aliases y devuelve lista ordenada (name, id, exe, score)."""
        apps = self._fetch_discord_apps_cached()
        candidates = []
        gnl = (game_name or "").lower()
        for app in apps:
            name = app.get("name", "") or ""
            aliases = app.get("aliases", []) or []
            score_name = difflib.SequenceMatcher(None, gnl, name.lower()).ratio()
            # score por alias más alta
            score_alias = 0.0
            for a in aliases:
                s = difflib.SequenceMatcher(None, gnl, (a or "").lower()).ratio()
                if s > score_alias:
                    score_alias = s
            score = max(score_name, score_alias)
            if score > 0.35:  # filtro mínimo para reducir ruido
                # buscar ejecutable win32 si existe
                exe = None
                for e in app.get("executables", []) or []:
                    if e.get("os") == "win32" and e.get("name"):
                        exe = e.get("name")
                        break
                candidates.append({
                    "name": name,
                    "id": app.get("id"),
                    "exe": exe,
                    "score": score,
                    "aliases": aliases
                })
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:max_candidates]

    def _apply_discord_match(self, game_key: str, match: dict):
        """Aplica (guarda) la coincidencia al games_config.json y al self.games_map en memoria."""
        try:
            if not match or "id" not in match:
                return False
            config_path = CONFIG_PATH_FILE.read_text(encoding="utf-8").strip()
            config_path = Path(config_path)
            games_config = safe_json_load(config_path) or {}

            entry = games_config.get(game_key, {}) or {}

            # CAMBIO AQUÍ: usar asignación directa en lugar de setdefault
            if match.get("exe"):
                entry["executable_path"] = match["exe"]
            if match.get("id"):
                entry["client_id"] = match["id"]  # ← ASIGNACIÓN DIRECTA
            games_config[game_key] = entry
            save_json(games_config, config_path)
            # actualizar en memoria
            self.games_map = games_config
            logger.info(f"✅ Discord match aplicado para '{game_key}': id={match.get('id')}, exe={match.get('exe')}")
            return True
        except Exception as e:
            logger.error(f"❌ Error aplicando discord match: {e}")
            return False
            
    def _show_match_dialog(self, game_key: str, candidates: list, timeout: int = DISCORD_ASK_TIMEOUT):
        """
        Muestra una ventana tkinter con las mejores coincidencias. Devuelve match seleccionado o None.
        Esta función corre en el hilo GUI (abre una ventana temporal).
        """
        selected = {"value": None}
        try:
            root = tk.Tk()
            root.withdraw()
            top = tk.Toplevel()
            top.title(f"Coincidencia Discord: {game_key}")
            top.attributes("-topmost", True)
            # Label
            tk.Label(top, text=f"Se encontró un nuevo juego: '{game_key}'.\nSelecciona la coincidencia correcta (si alguna):", justify="left").pack(padx=10, pady=6)
            lb = tk.Listbox(top, width=80, height=min(8, max(3, len(candidates))))
            lb.pack(padx=10, pady=(0,6))
            # llenar listbox con nombre (score) [exe]
            for c in candidates:
                exe = c.get("exe") or ""
                lb.insert(tk.END, f"{c['name']}  ({c['score']:.2f})  [{exe}]  id={c.get('id') or '—'}")
            # botones
            def on_confirm():
                sel = lb.curselection()
                if sel:
                    idx = sel[0]
                    selected["value"] = candidates[idx]
                top.destroy()
            def on_ignore():
                top.destroy()
            btn_frame = tk.Frame(top)
            tk.Button(btn_frame, text="Confirmar", command=on_confirm).pack(side="left", padx=6)
            tk.Button(btn_frame, text="Ignorar", command=on_ignore).pack(side="left")
            btn_frame.pack(pady=(0,10))

            def on_timeout():
                try:
                    top.destroy()
                except Exception:
                    pass
            top.after(int(timeout * 1000), on_timeout)

            top.protocol("WM_DELETE_WINDOW", on_ignore)
            root.mainloop()
        except Exception as e:
            logger.debug(f"Error en dialog match: {e}")
            return selected["value"]

    def _ask_discord_match_for_new_game(self, game_key: str):
        """
        Hilo que busca coincidencias en Discord y aplica/consulta:
        - Si top score >= DISCORD_AUTO_APPLY_THRESHOLD -> aplica sin preguntar
        - Si hay candidatos pero score < threshold -> pregunta al usuario mediante ventana
        - Si no hay candidatos -> no hace nada
        """
        try:
            logger.info(f"🔍 Buscando coincidencias en Discord para: '{game_key}'")
            candidates = self._find_discord_matches(game_key, max_candidates=6)
            
            if not candidates:
                logger.info(f"ℹ️ No se encontraron matches en Discord para '{game_key}'")
                return
            
            top = candidates[0]
            logger.info(f"🎯 Discord top candidate for '{game_key}': {top.get('name')} (score={top.get('score'):.2f})")
            
            # auto apply si muy seguro
            if top.get("score", 0) >= DISCORD_AUTO_APPLY_THRESHOLD:
                applied = self._apply_discord_match(game_key, top)
                if applied:
                    logger.info(f"🔁 Aplicado automaticamente match Discord: {top.get('name')} (score {top.get('score'):.2f})")
                return

            # Crear una ventana raíz temporal para el diálogo
            logger.info(f"🔄 Creando diálogo para '{game_key}'")
            
            # Ejecutar el diálogo directamente en este hilo con una nueva instancia de Tk
            sel = self._show_match_dialog_simple(game_key, candidates)
            
            if sel:
                logger.info(f"✅ Usuario seleccionó: {sel.get('name')}")
                applied = self._apply_discord_match(game_key, sel)
                if applied:
                    logger.info(f"🔁 Match aplicado exitosamente para '{game_key}'")
                else:
                    logger.error(f"❌ Falló al aplicar match para '{game_key}'")
            else:
                logger.info(f"ℹ️ Usuario ignoró match Discord para '{game_key}'")
                
        except Exception as e:
            logger.error(f"❌ Error en ask_discord_match_for_new_game: {e}")

    def _show_match_dialog_simple(self, game_key: str, candidates: list, timeout: int = DISCORD_ASK_TIMEOUT):
        """
        Versión simplificada del diálogo que crea su propia instancia de Tkinter
        """
        selected = {"value": None}
        
        try:
            # Crear ventana raíz
            root = tk.Tk()
            root.withdraw()  # Ocultar ventana principal
            
            # Crear diálogo
            top = tk.Toplevel(root)
            top.title(f"Coincidencia Discord: {game_key}")
            top.attributes("-topmost", True)
            
            # Centrar en pantalla
            top.update_idletasks()
            x = (top.winfo_screenwidth() - top.winfo_width()) // 2
            y = (top.winfo_screenheight() - top.winfo_height()) // 2
            top.geometry(f"+{x}+{y}")
            
            # Label
            tk.Label(top, text=f"Se encontró un nuevo juego: '{game_key}'.\nSelecciona la coincidencia correcta (si alguna):", 
                    justify="left").pack(padx=10, pady=6)
            
            # Listbox
            lb = tk.Listbox(top, width=80, height=min(8, max(3, len(candidates))))
            lb.pack(padx=10, pady=(0, 6))
            
            # Llenar listbox
            for c in candidates:
                exe = c.get("exe") or ""
                lb.insert(tk.END, f"{c['name']}  ({c['score']:.2f})  [{exe}]  id={c.get('id') or '—'}")
            
            # Botones
            def on_confirm():
                sel = lb.curselection()
                if sel:
                    idx = sel[0]
                    selected["value"] = candidates[idx]
                root.quit()
                root.destroy()
                
            def on_ignore():
                root.quit()
                root.destroy()
                
            btn_frame = tk.Frame(top)
            tk.Button(btn_frame, text="Confirmar", command=on_confirm).pack(side="left", padx=6)
            tk.Button(btn_frame, text="Ignorar", command=on_ignore).pack(side="left")
            btn_frame.pack(pady=(0, 10))
            
            # Seleccionar primer elemento por defecto
            lb.selection_set(0)
            lb.focus_set()
            
            # Manejar cierre de ventana
            top.protocol("WM_DELETE_WINDOW", on_ignore)
            
            # Timeout
            def on_timeout():
                try:
                    root.quit()
                    root.destroy()
                except:
                    pass
                    
            top.after(int(timeout * 1000), on_timeout)
            
            # Ejecutar el diálogo
            root.mainloop()
            
        except Exception as e:
            logger.error(f"❌ Error en show_match_dialog_simple: {e}")
        
        return selected["value"]

    def run_loop(self):
        logger.info("🟢 Iniciando monitor de presencia...")
        try:
            while True:
                if not self.is_geforce_running():
                    if getattr(self, "forced_game", None):
                        logger.info("Modo forzado desactivado ...")
                        self.forced_game = None
                    if self.last_game is not None:
                        logger.info("⚠️ GeForce NOW no está en ejecución — limpiando presencia.")
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
            try:
                self.rpc.clear()
            except Exception:
                pass
            try:
                self.rpc.close()
                logger.info("🔴 Discord RPC cerrado correctamente.")
            except Exception:
                pass
            self.close_fake_executable()
            sys.exit(0)

        except Exception as e:
            if str(e) not in (
                "'NoneType' object has no attribute 'get'",
                "cannot access local variable 'title' where it is not associated with a value",
            ):
                logger.error(f"❌ Error inesperado en el loop principal: {e}")
            try:
                self.rpc.clear()
            except Exception:
                pass
            try:
                self.rpc.close()
            except Exception:
                pass
            self.close_fake_executable()
            sys.exit(1)

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
                #if title and title.strip() == "GeForce NOW":
                    #return {
                    #    "name": "GeForce NOW",
                    #   "client_id": "1421154726023532544",
                    #  "executable_path": "ea sports fc 26/fc26.exe",
                    #   "image": "geforce_default"
                    #}

                clean = re.sub(r'\s*(en|on|in|via)?\s*GeForce\s*NOW.*$', '', title, flags=re.IGNORECASE).strip()
                clean = re.sub(r'[®™]', '', clean).strip()
                #if clean.lower() not in ["geforce now", "games", ""]:
                #    logger.debug(f"|: {clean}")

                
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
                    "image": "steam"
                }
                self.games_map[clean] = new_game
                config_path = CONFIG_PATH_FILE.read_text(encoding="utf-8").strip()
                config_path = Path(config_path)
                games_config = safe_json_load(config_path) or {}
                games_config[clean] = new_game
                save_json(games_config, config_path)
                updated = self.games_map.get(clean)
                if updated:
                    new_game = updated
                logger.info(f"🆕 Juego agregado a config: {clean} (AppID: {appid})")
                self.games_map = games_config

                try:
                    threading.Thread(
                        target=self._ask_discord_match_for_new_game,
                        args=(clean,),
                        daemon=True
                    ).start()
                except Exception as e:
                    logger.debug(f"no se pudo iniciar hilo de discord-match: {e}")
                return new_game

            
            return {'name': title, 'image': 'geforce_default', 'client_id': self.client_id}
        except Exception as e:
            if str(e) == "cannot access local variable 'title' where it is not associated with a value":
                self.log_once(f"⚠️ GeForce NOW está cerrado")
            else:
                logger.error(f"⚠️ Error detectando juego activo: {e}")

    def log_once(self, msg, level="info"):
        if msg != self.last_log_message:
            getattr(logger, level)(msg)
            self.last_log_message = msg

    def is_geforce_running(self) -> bool:
        try:
            for proc in psutil.process_iter(attrs=['name']):
                name = (proc.info.get('name') or "").lower()
                if "geforcenow" in name:
                    return True
        except Exception as e:
            logger.debug(f"Error comprobando procesos: {e}")
        return False
    
    def clear_forced_game(self):
        if self.forced_game:
            logger.info(f"🧹 Modo forzado desactivado: {self.forced_game.get('name')}")
            self.forced_game = None

    def update_presence(self, game_info: Optional[dict]):
        # Si hay un juego forzado, usarlo en lugar del juego detectado
        if getattr(self, "forced_game", None):
            game_info = self.forced_game
            # Log periódico para indicar que está en modo forzado
            current_time = time.time()
            if not hasattr(self, "_last_forced_log") or current_time - self._last_forced_log > 300:  # Cada 5 minutos
                logger.info(f"🔧 Modo forzado activo: {self.forced_game.get('name')}")
                self._last_forced_log = current_time

        # Evitar reconexión automática inmediata después de detener forzado
        if (hasattr(self, "_force_stop_time") and 
            getattr(self, "_last_forced_game", None) and 
            game_info and 
            game_info.get("name") == self._last_forced_game.get("name")):
            
            current_time = time.time()
            if current_time - self._force_stop_time < 10:  # Evitar por 10 segundos
                logger.debug(f"⏸️  Evitando reconexión automática a {game_info.get('name')} tras detener forzado")
                # Limpiar presencia temporalmente
                try:
                    self.rpc.clear()
                except Exception:
                    pass
                self.last_game = None
                return

        current_game = game_info or None
        game_changed = not self.is_same_game(self.last_game, current_game)
        
        # Obtener rich presence y group size
        status, group_size = None, None
        if current_game and current_game.get("steam_appid"):
            status, group_size = self.scraper.get_rich_presence()
        
        if current_game and current_game.get("name") in self.games_map:
            defaults = self.games_map[current_game["name"]]
            merged = {**defaults, **current_game}
            current_game = merged

        if current_game and current_game.get("name") is None:
            self.log_once("🛑 GeForce NOW está cerrado")
            self.close_fake_executable()
            try:
                self.rpc.clear()
            except Exception:
                pass
            self.last_game = None
            return

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

        client_id = current_game.get("client_id") or self.client_id
        
        # Solo cambiar client_id si no estamos en el período de evitación
        should_change_client = True
        if (hasattr(self, "_force_stop_time") and 
            getattr(self, "_last_forced_game", None) and 
            current_game and 
            current_game.get("name") == self._last_forced_game.get("name")):
            
            current_time = time.time()
            if current_time - self._force_stop_time < 10:
                should_change_client = False
                client_id = self.client_id  # Usar client_id por defecto

        if getattr(self.rpc, "client_id", None) != client_id and should_change_client:
            try:
                self.rpc.clear()
                self.rpc.close()
            except Exception:
                pass
            if client_id:
                self._connect_rpc(client_id)
                self.log_once(f"🔁 Cambiado client_id a {client_id}")

        # Procesar el estado dinámicamente basado en group_size
        def split_status(s):
            for sep in ["|", " - ", ":", "›", ">"]:
                if sep in s:
                    a, b = s.split(sep, 1)
                    return a.strip(), b.strip()
            return s.strip(), None

        details, state = (split_status(status) if status else (None, None))
        
        # Actualizar state basado en group_size
        if group_size is not None:
            if group_size == 1:
                state = TEXTS.get("playing_solo", "Playing solo")
            else:
                state = TEXTS.get("playing_in_group", f"On a Group ({group_size} players)")
        
        if not details and not current_game.get("client_id"):
            rn = current_game.get('name', '').strip().lower()
            if rn in ["geforce now", "Games", ""]:
                current_game["image"] = "lib"

        # Preparar party_size dinámicamente
        party_size_data = None
        if group_size is not None:
            # Si tenemos group_size, usarlo para party_size
            party_size_data = [group_size, 4]  # [current, max] - puedes ajustar el máximo según el juego
        elif current_game.get("party_size"):
            # Si el juego tiene party_size definido en la configuración
            party_size_data = current_game.get("party_size")

        presence_data = {
            "details": details,
            "state": state,
            "large_image": current_game.get('image', 'steam'),
            "large_text": current_game.get('name'),
            "small_image": current_game.get("icon_key") if current_game.get("icon_key") else None
        }
        
        # Agregar party_size solo si está disponible
        if party_size_data:
            presence_data["party_size"] = party_size_data

        try:
            self.rpc.update(**{k: v for k, v in presence_data.items() if v})
        except Exception as e:
            msg = str(e).lower()
            logger.error(f"❌ Error actualizando Presence: {e}")
            if "pipe was closed" in msg or "socket.send()" in msg:
                try:
                    time.sleep(5) 
                    self._connect_rpc(client_id)
                    logger.info("🔁 Reconectado con Discord RPC tras error de socket")
                except Exception as e2:
                    logger.error(f"❌ Falló la reconexión a Discord RPC: {e2}")

        self.last_game = dict(current_game) if isinstance(current_game, dict) else current_game
        
        # Limpiar el estado de evitación después del período
        if (hasattr(self, "_force_stop_time") and 
            time.time() - self._force_stop_time >= 10):
            if hasattr(self, "_last_forced_game"):
                del self._last_forced_game
            if hasattr(self, "_force_stop_time"):
                del self._force_stop_time

    def is_same_game(self, g1: Optional[dict], g2: Optional[dict]) -> bool:
        if g1 is None and g2 is None:
            return True
        if (g1 is None) != (g2 is None):
            return False
        for k in ("client_id", "executable_path", "name"):
            if g1.get(k) != g2.get(k):
                return False
        return True
    
    def close(self):
        if self.rpc:
            try:
                self.rpc.clear()
                self.rpc.close()
                self.close_fake_executable()
                
                
                logger.info("🔴 Discord RPC cerrado correctamente.")
            except Exception:
                pass

# ----------------- MAIN -----------------
def main():
    if not acquire_lock():
        show_message("Error", TEXTS.get('already_running', 'Another instance of the program is already running.'), kind="error")
        return
    use_tray = PYSTRAY_AVAILABLE
    if use_tray:
        try:
            tray_started = start_tray_icon(on_quit_callback=lambda: presence.close())
            if not tray_started:
                logger.info("Se usará notificación porque no se pudo iniciar tray.")
        except Exception as e:
            logger.debug(f"No se pudo iniciar tray: {e}")
            tray_started = False

    if not tray_started:
        logger.error("❌ No se pudo iniciar el tray. Instala pystray y Pillow.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--no-launch-geforce", action="store_true")
    parser.add_argument("--no-launch-discord", action="store_true")
    parser.add_argument("--verbose", action="store_true", help="Mostrar lista completa de juegos en carga")
    parser.add_argument("--no-keepalive", action="store_true", help="Desactivar keep-alive (si está activado)")
    parser.add_argument("--tray", action="store_true", help="Forzar uso de icono en bandeja (si está disponible)")
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
                            )

    global PRESENCE_INSTANCE, COOKIE_MANAGER
    PRESENCE_INSTANCE = presence
    COOKIE_MANAGER = cookie_mgr


    

    try:
        presence.run_loop()
    finally:
        # limpieza final
        stop_tray_icon()
        presence.close()

if __name__ == "__main__":
    main()

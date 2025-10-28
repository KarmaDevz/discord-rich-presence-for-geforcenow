import threading
import os
from pathlib import Path
import logging
from constants import LOG_FILE, ENV_PATH

try:
    import pystray
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except Exception:
    pystray = None
    Image = None
    ImageDraw = None
    PYSTRAY_AVAILABLE = False

logger = logging.getLogger('geforce_presence')

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


def start_tray_icon(assets_dir: Path, on_quit_callback, title="GeForceNOW Presence", presence_instance=None, cookie_manager=None, texts=None):
    img_path = assets_dir / "geforce.ico"
    global _tray_icon, _tray_thread
    if not PYSTRAY_AVAILABLE:
        logger.info("pystray/Pillow no disponibles; no se mostrará icono en bandeja.")
        return False

    def _quit_action(icon, item):
        logger.info("Cierre pedido desde icono de bandeja.")
        try:
            on_quit_callback()
        except Exception:
            pass
        try:
            icon.visible = False
            icon.stop()
        except Exception:
            pass
        try:
            if presence_instance is not None:
                presence_instance.close()
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
            from app_launcher import AppLauncher
            AppLauncher.launch_geforce_now()
        except Exception as e:
            logger.debug(f"Error abriendo GeForce NOW: {e}")

    def _obtain_cookie(icon, item):
        try:
            if cookie_manager is None:
                return
            val = cookie_manager.ask_and_obtain_cookie()
            if val:
                from utils import save_cookie_to_env
                save_cookie_to_env(Path(ENV_PATH), val)
        except Exception as e:
            logger.debug(f"Fallo al obtener cookie: {e}")

    def _force_game(icon, item):
        try:
            from tkinter import simpledialog, Tk
            root = Tk()
            root.iconbitmap(default=str(assets_dir / "geforce.ico"))
            root.title("GeForceNOW Presence")
            root.geometry("1x1+20000+20000")
            root.attributes("-topmost", True)
            root.update_idletasks()
            game_name = simpledialog.askstring("Forzar juego", "Nombre del juego:", parent=root)
            root.destroy()
            if not game_name or not presence_instance:
                return
            # Delegate to presence instance
            candidates = []
            gm = presence_instance.games_map or {}
            candidates = [k for k in gm if game_name.lower() in k.lower()]
            options = []
            if candidates:
                for k in candidates:
                    options.append((k, gm[k].get("client_id"), gm[k].get("executable_path")))
            else:
                disc = presence_instance._find_discord_matches(game_name, max_candidates=5)
                for c in disc:
                    options.append((c["name"], c["id"], c.get("exe")))
                    presence_instance._apply_discord_match(game_name, c)
            if not options:
                return
            # simple selection: pick first
            name, cid, exe = options[0]
            if cid:
                presence_instance.client_id = cid
                presence_instance._connect_rpc(cid)
            if exe:
                presence_instance.launch_fake_executable(exe)
            game_entry = presence_instance.games_map.get(name) or presence_instance.games_map.get("GeForce NOW")
            presence_instance.forced_game = {
                "name": game_entry.get("name", name),
                "client_id": cid or game_entry.get("client_id"),
                "executable_path": exe or game_entry.get("executable_path"),
            }

        except Exception as e:
            logger.debug(f"Error force_game: {e}")

    menu = pystray.Menu(
        pystray.MenuItem("Forzar juego...", _force_game),
        pystray.MenuItem("Obtener cookie de Steam", _obtain_cookie),
        pystray.MenuItem("Abrir GeForce NOW", _open_geforce),
        pystray.MenuItem("Abrir logs", _open_logs),
        pystray.MenuItem("Salir", _quit_action),
    )

    try:
        icon_img = Image.open(str(img_path)) if img_path.exists() else _create_default_icon_image()
        icon = pystray.Icon("geforce_presence", icon_img, title, menu)
    except Exception as e:
        logger.error(f"No se pudo crear Icon pystray: {e}")
        return False

    def run_icon():
        try:
            icon.run()
        except Exception as e:
            logger.debug(f"Icon tray error: {e}")

    _tray_icon = icon
    _tray_thread = threading.Thread(target=run_icon, daemon=True); _tray_thread.start()
    return True


def stop_tray_icon():
    global _tray_icon
    try:
        if _tray_icon:
            try:
                _tray_icon.stop()
            except Exception:
                pass
            _tray_icon = None
    except Exception:
        pass

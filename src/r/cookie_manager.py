import logging
import requests
import browser_cookie3
import time
from pathlib import Path
from utils import save_cookie_to_env
from constants import ENV_PATH
from typing import Optional
import os

logger = logging.getLogger('geforce_presence')


class CookieManager:
    def __init__(self, env_cookie: Optional[str] = None, test_url: str = ""):
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

    def ask_get_cookie(self, show_message_func) -> bool:
        res = show_message_func("Cookie", "The program will try to obtain your Steam cookie using Microsoft Edge. Make sure you are logged in to Steam in Edge.\n\nDo you want to continue?", kind="askyesno")
        return res

    def close_edge_processes(self):
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

    def get_cookie_with_selenium(self, service, headless: bool = False, profile_dir: str = "Default") -> Optional[str]:
        try:
            logger.info("🧩 Obteniendo cookie de Steam con Selenium (Edge)...")
            localapp = os.getenv("LOCALAPPDATA", "")
            user_data_dir = str(Path(localapp) / "Microsoft" / "Edge" / "User Data")
            if not Path(user_data_dir).exists():
                logger.error("❌ No se encontró la carpeta de perfiles de Edge.")
                return None

            from selenium.webdriver.edge.options import Options
            from selenium import webdriver
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
                    save_cookie_to_env(Path(ENV_PATH), val)
                    logger.debug(f"Cookie obtenida parcial: {val[:20]}... (longitud: {len(val)})")
                    logger.info("✅ Cookie obtenida con Selenium.")
                    return val
            driver.quit()
            logger.warning("⚠️ No se encontró 'steamLoginSecure' en la sesión de Steam.")
        except Exception as e:
            logger.error(f"⚠️ Error inesperado obteniendo cookie con Selenium: {e}")
        return None

    def get_steam_cookie(self, service) -> Optional[str]:
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

        c2 = self.get_cookie_with_selenium(service, headless=False)
        if c2 and self.validar_cookie(c2):
            return c2

        logger.error("❌ No se pudo obtener cookie de Steam automáticamente.")
        return None

    def ask_and_obtain_cookie(self, show_message_func, service) -> Optional[str]:
        try:
            should = show_message_func("Cookie", "The program will try to obtain your Steam cookie using Microsoft Edge. Make sure you are logged in to Steam in Edge.\n\nDo you want to continue?", kind="askyesno")
            if not should:
                logger.info("No se obtuvo cookie de Steam de forma interactiva.")
                return None
            c = self.get_cookie_from_edge_profile()
            if c and self.validar_cookie(c):
                save_cookie_to_env(Path(ENV_PATH), c)
                return c
            c2 = self.get_cookie_with_selenium(service, headless=False)
            if c2 and self.validar_cookie(c2):
                save_cookie_to_env(Path(ENV_PATH), c2)
                return c2
            logger.warning("No se pudo obtener cookie automáticamente tras solicitud del usuario.")
            return None
        except Exception as e:
            logger.error(f"Error en ask_and_obtain_cookie: {e}")
            return None
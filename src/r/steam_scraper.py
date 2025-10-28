import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import Optional

logger = logging.getLogger('geforce_presence')


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

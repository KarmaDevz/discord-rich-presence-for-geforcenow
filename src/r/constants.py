from pathlib import Path
import tempfile
import os
import time

LOCK_FILE = Path(tempfile.gettempdir()) / "geforce_presence.lock"
BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
LANG_DIR = BASE_DIR / "lang"
ASSETS_DIR = BASE_DIR / "assets"
driver_path = BASE_DIR / "tools" / "msedgedriver.exe"
LOG_FILE = LOGS_DIR / "geforce_presence.log"
ENV_PATH = BASE_DIR / ".env"
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